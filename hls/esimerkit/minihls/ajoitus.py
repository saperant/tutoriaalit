"""Ajoitus: kullekin operaatiolle kellojakso.

ASAP ja ALAP lasketaan yksikköviivemallilla (jokainen operaatio vie
yhden jakson). Varsinainen listaajoitus käyttää operaatioiden viiveitä
nanosekunteina, ketjuttaa peräkkäisiä operaatioita samaan jaksoon,
kunhan kellojakso riittää, ja noudattaa resurssirajoja.
Liukuhihnoitetussa silmukassa resurssit varataan modulo-
varaustaulukosta (jakso mod II).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .dfg import Dfg, Kantava, Reuna, Solmu, Vakio, Viite, operandit
from .puu import KaannosVirhe

# @alku viiveet
# Viiveet nanosekunteina (suuntaa-antavia, FPGA:n luokkaa).
VIIVEET = {
    "+": 2.0, "-": 2.0, "*": 6.0, "<": 2.0, "<=": 2.0, ">": 2.0,
    ">=": 2.0, "==": 1.5, "!=": 1.5, "&": 0.5, "|": 0.5, "^": 0.5,
    "~": 0.5, "valinta": 1.0, "<<": 3.0, ">>": 3.0,
    "lataa": 1.0, "tallenna": 1.0, "kirjoita_virta": 1.0,
}
RAM_ULOS = 1.5          # synkronisen RAMin data seuraavalla jaksolla
VIRTA_SISAAN = 1.0      # tulevan virran data jakson alusta
# @loppu viiveet


def viive(s: Solmu) -> float:
    vakio_operandi = any(isinstance(o, Vakio) for o in s.syotteet)
    if s.laji in ("<<", ">>", "&", "|", "^") and vakio_operandi:
        return 0.0                  # johdotusta tai vakiobittejä
    return VIIVEET.get(s.laji, 0.0)


# @alku resurssit
def resurssi(s: Solmu) -> str | None:
    """Rajallinen resurssi, jonka operaatio varaa yhdeksi jaksoksi."""
    if s.laji == "*":
        return "mul"
    if s.laji in ("+", "-"):
        return "add"
    if s.laji == "lataa":
        return f"{s.muisti}: lukuportti"
    if s.laji == "tallenna":
        return f"{s.muisti}: kirjoitusportti"
    if s.laji in ("lue_virta", "kirjoita_virta"):
        return f"{s.kohde}: virta"
    return None


def kapasiteetti(nimi: str, rajat: dict[str, int]) -> int:
    if nimi in rajat:
        return rajat[nimi]
    return 10**6 if nimi in ("mul", "add") else 1
# @loppu resurssit


# --- yksikköviivemalli -------------------------------------------------
def yksikko(s: Solmu) -> int:
    return 1 if viive(s) > 0 else 0


def asap(g: Dfg) -> dict[int, int]:
    tulos: dict[int, int] = {}
    reunat = {i: [r for r in g.reunat if r.kohde == i] for i in g.solmut}
    for i in sorted(g.solmut):
        s = g.solmut[i]
        jakso = 0
        for o in operandit(s):
            if isinstance(o, Viite):
                u = g.solmut[o.solmu]
                jakso = max(jakso, tulos[u.id] + yksikko(u))
        for r in reunat[i]:
            jakso = max(jakso, tulos[r.lahto] + r.viive)
        tulos[i] = jakso
    return tulos


def alap(g: Dfg, pituus: int) -> dict[int, int]:
    tulos: dict[int, int] = {}
    kayttajat = g.kayttajat()
    for i in sorted(g.solmut, reverse=True):
        s = g.solmut[i]
        jakso = pituus - yksikko(s)
        for k in kayttajat[i]:
            jakso = min(jakso, tulos[k] - yksikko(s))
        for r in g.reunat:
            if r.lahto == i:
                jakso = min(jakso, tulos[r.kohde] - r.viive)
        tulos[i] = jakso
    return tulos


def yksikkopituus(g: Dfg, a: dict[int, int]) -> int:
    return max((a[i] + yksikko(s) for i, s in g.solmut.items()), default=0)


# --- listaajoitus ----------------------------------------------------
# @alku ajoitus
@dataclass
class Ajoitus:
    jakso: dict[int, int] = field(default_factory=dict)
    johto: dict[int, int] = field(default_factory=dict)  # tulos johdossa
    saapuu: dict[int, float] = field(default_factory=dict)
    pituus: int = 0
    ii: int = 0


def listaa(g: Dfg, kello: float, rajat: dict[str, int],
           ii: int | None = None,
           alarajat: dict[int, int] | None = None) -> Ajoitus:
    """Jakso kerrallaan etenevä listaajoitus. Valmiista operaatioista
    sijoitetaan ensin kiireellisin (pienin ALAP-jakso). Alarajat
    estävät solmun sijoittamisen liian aikaisin."""
    alarajat = alarajat or {}
    a = asap(g)
    prioriteetti = alap(g, yksikkopituus(g, a))
    odottavat = sorted((i for i, s in g.solmut.items()
                        if s.laji != "muuttuja"),
                       key=lambda i: (prioriteetti[i], i))
    t = Ajoitus()
    kaytossa: dict[tuple[str, int], int] = {}
    reunat = {i: [r for r in g.reunat if r.kohde == i] for i in g.solmut}
    jakso = 0
    while odottavat:
        sijoitettiin = True
        while sijoitettiin:
            sijoitettiin = False
            for i in odottavat:
                if alarajat.get(i, 0) > jakso:
                    continue
                if sijoita(g, t, g.solmut[i], jakso, kello, rajat, ii,
                           kaytossa, reunat[i]):
                    odottavat.remove(i)
                    sijoitettiin = True
                    break
        jakso += 1
        if jakso > 100_000:
            raise KaannosVirhe(0, "ajoitus ei valmistu")
    t.pituus = max((max(t.jakso[i], t.johto[i]) + 1 for i in g.solmut),
                   default=1)
    t.ii = ii if ii is not None else t.pituus
    return t
# @loppu ajoitus


def sijoita(g: Dfg, t: Ajoitus, s: Solmu, jakso: int, kello: float,
            rajat: dict[str, int], ii: int | None,
            kaytossa: dict[tuple[str, int], int],
            reunat: list[Reuna]) -> bool:
    if s.laji == "muuttuja":
        return False                # sijoitetaan ensimmäisen käyttäjän mukaan
    alku = 0.0
    luettavat: list[int] = []
    for o in operandit(s):
        if not isinstance(o, Viite):
            continue
        u = g.solmut[o.solmu]
        if u.laji == "muuttuja":
            if u.id not in t.jakso:
                luettavat.append(u.id)
            continue
        if u.id not in t.johto or t.johto[u.id] > jakso:
            return False
        if t.johto[u.id] == jakso:
            alku = max(alku, t.saapuu[u.id])
    for r in reunat:
        if r.lahto not in t.jakso or jakso < t.jakso[r.lahto] + r.viive:
            return False
    loppu = alku + viive(s)
    if loppu > kello:
        if alku > 0:
            return False            # ei mahdu tähän jaksoon ketjutettuna
        raise KaannosVirhe(s.rivi, f"operaatio {s.laji} ({viive(s)} ns) "
                           f"ei mahdu {kello} ns:n kellojaksoon")
    nimi = resurssi(s)
    if nimi is not None:
        paikka = (nimi, jakso if ii is None else jakso % ii)
        if kaytossa.get(paikka, 0) >= kapasiteetti(nimi, rajat):
            return False
        kaytossa[paikka] = kaytossa.get(paikka, 0) + 1
    for luku in luettavat:
        t.jakso[luku] = t.johto[luku] = jakso
        t.saapuu[luku] = 0.0
    t.jakso[s.id] = jakso
    if s.laji == "lataa":
        t.johto[s.id], t.saapuu[s.id] = jakso + 1, RAM_ULOS
    elif s.laji == "lue_virta":
        t.johto[s.id], t.saapuu[s.id] = jakso, VIRTA_SISAAN
    else:
        t.johto[s.id], t.saapuu[s.id] = jakso, loppu
    return True


# --- liukuhihnoitus ----------------------------------------------------
# @alku modulo
def res_mii(g: Dfg, rajat: dict[str, int]) -> tuple[int, str]:
    """Resurssien asettama alaraja aloitusvälille."""
    maarat: dict[str, int] = {}
    for s in g.solmut.values():
        nimi = resurssi(s)
        if nimi is not None:
            maarat[nimi] = maarat.get(nimi, 0) + 1
    paras, syy = 1, ""
    for nimi, maara in sorted(maarat.items()):
        mii = math.ceil(maara / kapasiteetti(nimi, rajat))
        if mii > paras:
            paras, syy = mii, f"{nimi}, {maara} käyttöä"
    return paras, syy


def rikotut(g: Dfg, t: Ajoitus, ii: int) -> list[Kantava]:
    return [k for k in g.kantavat if t.jakso[k.kohde] + ii * k.etaisyys
            < t.jakso[k.lahto] + k.viive]


def liukuhihnoita(g: Dfg, kello: float, rajat: dict[str, int],
                  pyydetty: int) -> tuple[Ajoitus, list[str]]:
    """Kokeilee aloitusvälejä II = max(pyydetty, ResMII), ... kunnes
    silmukan kantamat riippuvuudet toteutuvat. Jos riippuvuus ei
    toteudu, sen kohdetta (esim. muuttujan lukua) yritetään ensin
    siirtää myöhemmäksi samalla II:llä."""
    mii, syy = res_mii(g, rajat)
    syyt = [syy] if mii > pyydetty else []
    ii = max(pyydetty, mii)
    kayttajat = g.kayttajat()
    while True:
        alarajat: dict[int, int] = {}
        for _ in range(len(g.solmut) + 1):
            t = listaa(g, kello, rajat, ii, alarajat)
            virheet = rikotut(g, t, ii)
            if not virheet:
                return t, syyt
            muuttui = False
            for k in virheet:
                tarve = t.jakso[k.lahto] + k.viive - ii * k.etaisyys
                kohteet = kayttajat[k.kohde] \
                    if g.solmut[k.kohde].laji == "muuttuja" else [k.kohde]
                for i in kohteet:
                    if alarajat.get(i, 0) < tarve:
                        alarajat[i] = tarve
                        muuttui = True
            if not muuttui:
                break
        syyt = sorted({k.syy for k in virheet})
        ii += 1
# @loppu modulo

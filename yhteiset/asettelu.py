"""Taitopuukartan säteittäinen asettelu.

Taidot sijoitetaan kehille niiden tason mukaan: tason 1 taidot ovat
sisimmällä kehällä, ja jokainen seuraava taso on yhtä kehää ulompana.
Kukin erikoistunut alue saa oman kulmasektorinsa. Perusta- ja
matematiikka-alueilla ei ole omaa sektoria, vaan niiden taidot
asettuvat niiden taitojen suuntaan, joita ne mahdollistavat.

Kulmat haetaan iteroimalla: jokainen taito vetää naapureitaan
(esitietoja ja seuraajia) puoleensa, oma sektori vetää taitoa kohti
keskikohtaansa, ja saman kehän taidot työnnetään erilleen niin, että
niiden väli on vähintään VALI pikseliä. Asettelu on deterministinen.
"""

from __future__ import annotations

import itertools
import math

SADE_1 = 200      # tason 1 kehän säde
KEHAVALI = 170    # kehien etäisyys toisistaan
VALI = 168         # pienin kaarietäisyys saman kehän taitojen välillä
SEKTORIVETO = 1.6
VAPAAT_ALUEET = ("perusta", "matematiikka")


def kulmaero(a: float, b: float) -> float:
    """Pienin etumerkillinen kulmaero b - a välillä (-pi, pi]."""
    return (b - a + math.pi) % (2 * math.pi) - math.pi


def keskikulma(kulmat: list[tuple[float, float]]) -> float:
    """Painotettu ympyräkeskiarvo listasta (kulma, paino)."""
    x = sum(p * math.cos(k) for k, p in kulmat)
    y = sum(p * math.sin(k) for k, p in kulmat)
    return math.atan2(y, x)


def sade(taso: int) -> float:
    return SADE_1 + (taso - 1) * KEHAVALI


def sektorijarjestys(puu) -> list[str]:
    """Valitsee erikoistuneiden alueiden järjestyksen kehällä niin, että
    toisistaan riippuvat alueet ovat lähekkäin."""
    alueet = [a for a in puu.alueet if a not in VAPAAT_ALUEET]
    painot: dict[tuple[str, str], int] = {}
    for t in puu.taidot.values():
        for e in t.edellyttaa:
            a, b = puu.taidot[e].alue, t.alue
            if a != b and a in alueet and b in alueet:
                avain = tuple(sorted((a, b)))
                painot[avain] = painot.get(avain, 0) + 1
    paras, paras_hinta = alueet, math.inf
    eka = alueet[0]   # kierron symmetria: ensimmäinen kiinnitetään
    for loput in itertools.permutations(alueet[1:]):
        jarjestys = (eka, *loput)
        paikka = {a: i for i, a in enumerate(jarjestys)}
        n = len(jarjestys)
        hinta = 0
        for (a, b), p in painot.items():
            d = abs(paikka[a] - paikka[b])
            hinta += p * min(d, n - d)
        if hinta < paras_hinta:
            paras, paras_hinta = list(jarjestys), hinta
    return paras


def aseta(puu) -> tuple[dict[str, tuple[float, float]], dict[str, float]]:
    """Palauttaa taitojen koordinaatit ja alueiden sektorikeskukset."""
    jarjestys = sektorijarjestys(puu)
    koot = {a: sum(1 for t in puu.taidot.values() if t.alue == a)
            for a in jarjestys}
    yhteensa = sum(koot.values())
    keskukset: dict[str, float] = {}
    alku = -math.pi / 2   # ensimmäinen sektori alkaa ylhäältä
    for a in jarjestys:
        leveys = 2 * math.pi * koot[a] / yhteensa
        keskukset[a] = alku + leveys / 2
        alku += leveys

    naapurit = {tid: list(t.edellyttaa) + list(t.seuraajat)
                for tid, t in puu.taidot.items()}

    kulma: dict[str, float] = {}
    for tid, t in puu.taidot.items():
        if t.alue in keskukset:
            kulma[tid] = keskukset[t.alue]
    # Vapaiden alueiden alkuarvo: jälkeläisten sektorien keskiarvo.
    for tid, t in puu.taidot.items():
        if tid not in kulma:
            jalk = [kulma[j] for j in puu.jalkelaiset(tid) if j in kulma]
            kulma[tid] = keskikulma([(k, 1.0) for k in jalk]) if jalk \
                else 0.0

    kehat: dict[int, list[str]] = {}
    for tid, t in puu.taidot.items():
        kehat.setdefault(t.taso, []).append(tid)
    for lista in kehat.values():
        lista.sort()

    for kierros in range(300):
        jaahdytys = 1.0 - kierros / 300
        uusi = {}
        for tid, t in puu.taidot.items():
            vedot = [(kulma[n], 1.0) for n in naapurit[tid]]
            if t.alue in keskukset:
                vedot.append((keskukset[t.alue], SEKTORIVETO))
            if not vedot:
                uusi[tid] = kulma[tid]
                continue
            tavoite = keskikulma(vedot)
            uusi[tid] = kulma[tid] + 0.5 * jaahdytys * kulmaero(
                kulma[tid], tavoite)
        kulma = uusi
        for taso, lista in kehat.items():
            levita(lista, kulma, VALI / sade(taso))

    sijainnit = {tid: (round(sade(t.taso) * math.cos(kulma[tid]), 1),
                       round(sade(t.taso) * math.sin(kulma[tid]), 1))
                 for tid, t in puu.taidot.items()}
    return sijainnit, keskukset


def levita(lista: list[str], kulma: dict[str, float], minimi: float):
    """Työntää saman kehän taidot erilleen säilyttäen järjestyksen."""
    if len(lista) < 2:
        return
    minimi = min(minimi, 2 * math.pi / len(lista))
    for _ in range(60):
        jarj = sorted(lista, key=lambda t: kulma[t] % (2 * math.pi))
        siirretty = False
        for i, a in enumerate(jarj):
            b = jarj[(i + 1) % len(jarj)]
            vali = (kulma[b] - kulma[a]) % (2 * math.pi)
            if vali < minimi - 1e-9:
                vaje = (minimi - vali) / 2
                kulma[a] -= vaje
                kulma[b] += vaje
                siirretty = True
        if not siirretty:
            break


def reitit(puu, sijainnit) -> list[dict]:
    """Piirilevyn johdinvetoja muistuttavat reitit esitiedoista taitoihin.

    Reitti lähtee esitiedosta säteen suuntaisesti, kiertää kaarena
    kohteen kehän sisäpuolella ja nousee säteen suuntaisesti kohteeseen.
    Saman kehävälin kaaret jaetaan kaistoille niin, että toisiaan
    kulmasuunnassa leikkaavat kaaret kulkevat eri säteillä.
    Keskipisteestä ("alku") vedetään suorat reitit tason 1 taitoihin.
    """
    def napa(tid):
        x, y = sijainnit[tid]
        return math.atan2(y, x)

    kaaret = []
    for t in puu.taidot.values():
        for e in t.edellyttaa:
            a0, a1 = napa(e), napa(t.id)
            kaaret.append({"a": e, "b": t.id, "alku": a0,
                           "ero": kulmaero(a0, a1), "taso": t.taso})

    # Kaistat kehäväleittäin: ahne välien väritys.
    valit: dict[int, list[dict]] = {}
    for k in kaaret:
        valit.setdefault(k["taso"], []).append(k)
    for taso, lista in valit.items():
        def vali(k):
            a = k["alku"] if k["ero"] >= 0 else k["alku"] + k["ero"]
            return a, a + abs(k["ero"])
        lista.sort(key=lambda k: (-abs(k["ero"]), vali(k)[0]))
        kaistat: list[list[tuple[float, float]]] = []
        for k in lista:
            v0, v1 = vali(k)
            for i, varatut in enumerate(kaistat):
                if all(not leikkaa(v0, v1, a, b) for a, b in varatut):
                    varatut.append((v0, v1))
                    k["kaista"] = i
                    break
            else:
                kaistat.append([(v0, v1)])
                k["kaista"] = len(kaistat) - 1
        sisa = sade(taso - 1) + 28
        ulko = sade(taso) - 30
        n = len(kaistat)
        for k in lista:
            # Pisimmät kaaret ulommille kaistoille.
            osuus = (k["kaista"] + 1) / (n + 1)
            k["r"] = ulko - osuus * (ulko - sisa)

    tulos = []
    for k in kaaret:
        ra = sade(puu.taidot[k["a"]].taso)
        rb = sade(k["taso"])
        a0, d = k["alku"], k["ero"]
        a1 = a0 + d
        r = k["r"]
        p = [(ra * math.cos(a0), ra * math.sin(a0)),
             (r * math.cos(a0), r * math.sin(a0)),
             (r * math.cos(a1), r * math.sin(a1)),
             (rb * math.cos(a1), rb * math.sin(a1))]
        lakaisu = 1 if d >= 0 else 0
        polku = (f"M{p[0][0]:.1f} {p[0][1]:.1f}L{p[1][0]:.1f} {p[1][1]:.1f}"
                 f"A{r:.1f} {r:.1f} 0 0 {lakaisu} {p[2][0]:.1f} "
                 f"{p[2][1]:.1f}L{p[3][0]:.1f} {p[3][1]:.1f}")
        if abs(d) < 1e-3:
            polku = (f"M{p[0][0]:.1f} {p[0][1]:.1f}"
                     f"L{p[3][0]:.1f} {p[3][1]:.1f}")
        tulos.append({"a": k["a"], "b": k["b"], "d": polku})

    for t in puu.taidot.values():
        if not t.edellyttaa:
            x, y = sijainnit[t.id]
            tulos.append({"a": "alku", "b": t.id,
                          "d": f"M0 0L{x:.1f} {y:.1f}"})
    return tulos


def leikkaa(a0: float, a1: float, b0: float, b1: float) -> bool:
    """Leikkaavatko kulmavälit toisiaan (ympyrällä)?"""
    vara = 0.04
    for siirto in (-2 * math.pi, 0.0, 2 * math.pi):
        if a0 < b1 + siirto + vara and b0 + siirto < a1 + vara:
            return True
    return False

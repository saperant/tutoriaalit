"""minihls: opetuskäyttöinen korkean tason synteesityökalu.

Käyttö:
    python3 -m minihls ydin.cpp --top nimi [--kello 10] [--ulos hak]
                       [--dfg] [--asap] [--ajoitus] [--paine]
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from .ajoitus import listaa, liukuhihnoita
from .dfg import Jako, Rakentaja, Silmukkatieto
from .jasennin import jasenna
from .muunnokset import Lehti, Ulompi, alueet, avaa, luetut
from .puu import Funktio, KaannosVirhe, Pragma
from .raportti import ajoitus, asap_alap, dfg, yhteenveto
from .sidonta import Lehtiajoitus, sido_kertojat
from .testipenkki import testipenkki
from .verilog import Tuottaja


# @alku pragmat
def funktion_pragmat(f: Funktio) -> tuple[dict[str, Jako], dict[str, int],
                                          dict[str, int | None]]:
    """array_partition, allocation ja dependence funktion pragmoista."""
    jaot: dict[str, Jako] = {}
    rajat: dict[str, int] = {}
    riippumattomat: dict[str, int | None] = {}
    for p in f.pragmat:
        a = p.asetukset
        if p.laji == "array_partition":
            jaot[vaadi(p, "variable")] = Jako(a.get("type", "complete"),
                                              int(a.get("factor", "1")))
        elif p.laji == "allocation":
            rajat[vaadi(p, "instances")] = int(vaadi(p, "limit"))
        elif p.laji == "dependence":
            taulu = vaadi(p, "variable")
            if a.get("dependent") == "false":
                riippumattomat[taulu] = None
            else:
                riippumattomat[taulu] = int(vaadi(p, "distance"))
        elif p.laji != "interface":
            raise KaannosVirhe(p.rivi, f"tuntematon pragma {p.laji}")
    for nimi, jako in jaot.items():
        paikallinen = nimi in f.paikalliset
        if jako.laji not in ("cyclic", "block", "complete") or (
                jako.laji == "complete" and not paikallinen) or (
                not paikallinen and f.parametri(nimi) is None):
            raise KaannosVirhe(0, f"array_partition {nimi}: tuntematon "
                               "taulukko tai jakotapa")
    return jaot, rajat, riippumattomat
# @loppu pragmat


def vaadi(p: Pragma, avain: str) -> str:
    if not p.asetukset.get(avain):
        raise KaannosVirhe(p.rivi, f"{p.laji}: puuttuu {avain}=")
    return p.asetukset[avain]


def lehdet_ja_ulommat(rakenne: list[Lehti | Ulompi],
                      ulommat: list[Silmukkatieto],
                      tulos: list[tuple[Lehti, list[Silmukkatieto]]]) -> None:
    for alue in rakenne:
        if isinstance(alue, Lehti):
            tulos.append((alue, list(ulommat)))
        else:
            tieto = Silmukkatieto(alue.nimi, alue.muuttuja, alue.alku,
                                  alue.askel, alue.kierrokset)
            lehdet_ja_ulommat(alue.runko, [*ulommat, tieto], tulos)


# @alku vuo
@dataclass
class Synteesi:
    lehdet: list[Lehtiajoitus]
    rakenne: list[Lehti | Ulompi]
    kartta: dict[int, Lehtiajoitus]
    jaot: dict[str, Jako]
    kertojat: dict[int, int]
    toistot: dict[int, int]


def syntetisoi(f: Funktio, kello: float) -> Synteesi:
    jaot, rajat, riippumattomat = funktion_pragmat(f)
    rakenne = alueet(avaa(f.runko))                   # 1. muunnokset
    parit: list[tuple[Lehti, list[Silmukkatieto]]] = []
    lehdet_ja_ulommat(rakenne, [], parit)
    tulokset: list[Lehtiajoitus] = []
    kartta: dict[int, Lehtiajoitus] = {}
    toistot: dict[int, int] = {}
    seuraava = 0
    for numero, (lehti, ulommat) in enumerate(parit, start=1):
        muut = [x for x, _ in parit if x is not lehti]
        elavat = set().union(*(luetut(x.lauseet) for x in muut))
        r = Rakentaja(f, lehti, ulommat, jaot, riippumattomat, seuraava)
        r.lauseet(lehti.lauseet)                      # 2. tietovuograafi
        g = r.valmis(elavat)
        seuraava = r.seuraava
        syyt: list[str] = []
        if lehti.ii is not None and lehti.kierrokset > 1:
            t, syyt = liukuhihnoita(g, kello, rajat, lehti.ii)  # 3.
        else:
            t = listaa(g, kello, rajat)
        x = Lehtiajoitus(numero, lehti.nimi, g, t, lehti.kierrokset,
                         lehti.alku, lehti.askel, lehti.ii, syyt)
        tulokset.append(x)
        kartta[id(lehti)] = x
        toistot[numero] = 1
        for u in ulommat:
            toistot[numero] *= u.kierrokset
    kertojat = sido_kertojat(tulokset)                # 4. sidonta
    return Synteesi(tulokset, rakenne, kartta, jaot, kertojat, toistot)
# @loppu vuo


def virtamaarat(lehdet: list[Lehtiajoitus],
                toistot: dict[int, int]) -> dict[str, int]:
    maarat: dict[str, int] = {}
    for x in lehdet:
        for s in x.g.solmut.values():
            if s.laji in ("lue_virta", "kirjoita_virta"):
                maarat[s.kohde] = maarat.get(s.kohde, 0) + \
                    x.kierrokset * toistot[x.numero]
    return maarat


def paaohjelma(argumentit: list[str]) -> int:
    jasentaja = argparse.ArgumentParser(prog="minihls")
    jasentaja.add_argument("lahde", type=Path)
    jasentaja.add_argument("--top", required=True)
    jasentaja.add_argument("--kello", type=float, default=10.0)
    jasentaja.add_argument("--ulos", type=Path)
    for valitsin in ("--dfg", "--asap", "--ajoitus"):
        jasentaja.add_argument(valitsin, nargs="?", const="*",
                               metavar="ALUE")
    jasentaja.add_argument("--paine", action="store_true")
    a = jasentaja.parse_args(argumentit)
    try:
        funktiot = {f.nimi: f for f in jasenna(a.lahde.read_text("utf-8"))}
        if a.top not in funktiot:
            raise KaannosVirhe(0, f"funktiota {a.top} ei löydy")
        f = funktiot[a.top]
        s = syntetisoi(f, a.kello)
        lehdet, toistot, kertojat = s.lehdet, s.toistot, s.kertojat
        tuottaja = Tuottaja(f, s.jaot, lehdet, s.rakenne, s.kartta,
                            kertojat)
        verilog = tuottaja.moduuli()
    except KaannosVirhe as virhe:
        print(f"virhe: {a.lahde.name}: {virhe}")
        return 1
    for x in lehdet:
        if a.dfg in ("*", x.nimi):
            tulosta(f"tietovuograafi: {x.nimi}", dfg(x.g))
        if a.asap in ("*", x.nimi):
            tulosta(f"ASAP ja ALAP: {x.nimi}", asap_alap(x.g))
        if a.ajoitus in ("*", x.nimi):
            tulosta("ajoitus", ajoitus(x, kertojat))
    kertojia = len(set(kertojat.values()))
    tulosta("", yhteenveto(f.nimi, a.kello, lehdet, toistot, kertojia))
    if a.ulos is not None:
        a.ulos.mkdir(parents=True, exist_ok=True)
        (a.ulos / f"{f.nimi}.v").write_text(verilog, "utf-8")
        (a.ulos / "tb.sv").write_text(
            testipenkki(tuottaja, virtamaarat(lehdet, toistot), a.paine),
            "utf-8")
    return 0


def tulosta(otsikko: str, rivit: list[str]) -> None:
    if otsikko:
        print(f"== {otsikko}")
    print("\n".join(rivit))


if __name__ == "__main__":
    sys.exit(paaohjelma(sys.argv[1:]))

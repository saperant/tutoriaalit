"""Rekisterikartta CSV:stä C-otsakkeeksi.

Laitteistosuunnittelija ylläpitää rekisterikarttaa taulukkona, ja
ohjelmisto tarvitsee siitä vakiot. Generoimalla otsake samasta
lähteestä vältetään käsin kopioinnin virheet. Generaattori tarkistaa
kartan ennen kuin kirjoittaa mitään.
"""

import argparse
import csv
import sys
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class Kentta:
    rekisteri: str
    osoite: int
    nimi: str
    ylin: int
    alin: int
    paasy: str
    kuvaus: str

    @property
    def maski(self) -> int:
        return ((1 << (self.ylin - self.alin + 1)) - 1) << self.alin


# @alku luku
def lue(rivit: Iterable[str]) -> list[Kentta]:
    kentat = []
    for rivi in csv.DictReader(rivit):
        ylin, _, alin = rivi["bitit"].partition(":")
        kentat.append(Kentta(
            rivi["rekisteri"].strip().upper(), int(rivi["osoite"], 0),
            rivi["kentta"].strip().upper(), int(ylin),
            int(alin or ylin), rivi["paasy"].strip().upper(),
            rivi["kuvaus"].strip()))
    return kentat


def tarkista(kentat: list[Kentta]) -> list[str]:
    virheet = []
    osoitteet: dict[int, str] = {}
    varatut: dict[str, int] = {}
    for k in kentat:
        tunnus = f"{k.rekisteri}.{k.nimi}"
        if k.osoite % 4:
            virheet.append(f"{tunnus}: osoite {k.osoite:#x} ei ole "
                           "4:llä jaollinen")
        if osoitteet.setdefault(k.osoite, k.rekisteri) != k.rekisteri:
            virheet.append(f"{tunnus}: osoite {k.osoite:#x} on jo "
                           f"rekisterillä {osoitteet[k.osoite]}")
        if not 0 <= k.alin <= k.ylin <= 31:
            virheet.append(f"{tunnus}: bitit {k.ylin}:{k.alin}")
        if k.paasy not in {"RO", "RW", "W1C"}:
            virheet.append(f"{tunnus}: tuntematon pääsy {k.paasy}")
        if varatut.get(k.rekisteri, 0) & k.maski:
            virheet.append(f"{tunnus}: bitit päällekkäin")
        varatut[k.rekisteri] = varatut.get(k.rekisteri, 0) | k.maski
    return virheet
# @loppu luku


# @alku otsake
def otsake(kentat: list[Kentta], etuliite: str) -> str:
    vahti = f"{etuliite}_REKISTERIT_H"
    r = ["/* Generoitu rekisterikartasta. Älä muokkaa käsin. */",
         f"#ifndef {vahti}", f"#define {vahti}", ""]
    nahdyt: set[str] = set()
    for k in kentat:
        nimi = f"{etuliite}_{k.rekisteri}"
        if k.rekisteri not in nahdyt:
            nahdyt.add(k.rekisteri)
            r.append(f"#define {nimi}_OFFSET 0x{k.osoite:02X}u")
        r.append(f"/* {k.nimi} [{k.ylin}:{k.alin}] {k.paasy}: "
                 f"{k.kuvaus} */")
        r.append(f"#define {nimi}_{k.nimi}_POS {k.alin}u")
        r.append(f"#define {nimi}_{k.nimi}_MASK 0x{k.maski:08X}u")
    r += ["", f"#endif /* {vahti} */"]
    return "\n".join(r) + "\n"
# @loppu otsake


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--etuliite", required=True)
    args = p.parse_args()
    kentat = lue(sys.stdin)
    if virheet := tarkista(kentat):
        for v in virheet:
            print(f"virhe: {v}", file=sys.stderr)
        return 1
    sys.stdout.write(otsake(kentat, args.etuliite.upper()))
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""CMOS-portti kytkinmallina.

nMOS-transistori johtaa, kun sen hila on 1, ja pMOS, kun hila on 0.
Ylösveto (pMOS-verkko) yhdistää lähdön käyttöjännitteeseen ja alasveto
(nMOS-verkko) maahan. Oikein suunnitellussa portissa täsmälleen toinen
verkko johtaa kaikilla syötteillä.
"""

from collections.abc import Callable
from dataclasses import dataclass
from itertools import product

Verkko = Callable[[dict[str, int]], bool]


# @alku kytkimet
def nmos(hila: str) -> Verkko:
    return lambda x: x[hila] == 1


def pmos(hila: str) -> Verkko:
    return lambda x: x[hila] == 0


def sarja(*osat: Verkko) -> Verkko:
    return lambda x: all(o(x) for o in osat)


def rinnan(*osat: Verkko) -> Verkko:
    return lambda x: any(o(x) for o in osat)
# @loppu kytkimet


@dataclass
class Cmos:
    nimi: str
    ylos: Verkko        # pMOS-verkko käyttöjännitteeseen
    alas: Verkko        # nMOS-verkko maahan


# @alku nand
NAND = Cmos("NAND",
            ylos=rinnan(pmos("a"), pmos("b")),
            alas=sarja(nmos("a"), nmos("b")))
NOR = Cmos("NOR",
           ylos=sarja(pmos("a"), pmos("b")),
           alas=rinnan(nmos("a"), nmos("b")))
# @loppu nand
# Virheellinen portti: alasvetoverkko on rinnan eikä sarjassa.
RIKKI = Cmos("RIKKI",
             ylos=rinnan(pmos("a"), pmos("b")),
             alas=rinnan(nmos("a"), nmos("b")))


# @alku lahto
def lahto(portti: Cmos, x: dict[str, int]) -> str:
    ylos, alas = portti.ylos(x), portti.alas(x)
    if ylos and alas:
        return "oikosulku"
    if not ylos and not alas:
        return "kelluva"
    return "1" if ylos else "0"
# @loppu lahto


def main() -> None:
    for portti in (NAND, NOR, RIKKI):
        rivit = []
        for a, b in product((0, 1), repeat=2):
            rivit.append(f"{a}{b}->{lahto(portti, {'a': a, 'b': b})}")
        print(f"{portti.nimi:5}: " + "  ".join(rivit))


if __name__ == "__main__":
    main()

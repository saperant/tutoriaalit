"""Uudelleenkäyttöetäisyyksien jakauma kunkin ytimen jäljestä.

Käyttö: python3 02-uudelleenkaytto.py JÄLKIHAKEMISTO
"""

import sys
from pathlib import Path

from arkki.jalki import AARETON, etaisyydet, lue_jalki, rivit

YTIMET = ["virta", "naiivi", "lohkottu", "lista"]
# @alku luokat
# Etäisyysluokat riveinä (64 B): 64 riviä = 4 KiB, 512 riviä = 32 KiB.
RAJAT = [1, 8, 64, 512]
OTSIKOT = ["0", "1-7", "8-63", "64-511", ">=512", "inf"]


def luokittele(d: int) -> int:
    if d == AARETON:
        return len(RAJAT) + 1
    return sum(1 for raja in RAJAT if d >= raja)
# @loppu luokat


def main() -> None:
    hakemisto = Path(sys.argv[1])
    print(f"{'ydin':<9} {'viitt':>6} {'rivejä':>6}"
          + "".join(f"{o:>8}" for o in OTSIKOT))
    for ydin in YTIMET:
        # @alku analyysi
        r = rivit(lue_jalki(hakemisto / f"{ydin}.txt"))
        maarat = [0] * len(OTSIKOT)
        for d in etaisyydet(r):
            maarat[luokittele(d)] += 1
        # @loppu analyysi
        osuudet = "".join(f"{100 * m / len(r):7.1f}%" for m in maarat)
        print(f"{ydin:<9} {len(r):>6} {len(set(r)):>6}{osuudet}")


if __name__ == "__main__":
    main()

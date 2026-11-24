"""Hutikäyrät yhdellä läpikäynnillä ja vertailu suoraan simulointiin.

Käyttö: python3 02-hutikayra.py JÄLKIHAKEMISTO
"""

import sys
from pathlib import Path

from arkki.jalki import etaisyydet, hutikayra, lru_hudit, lue_jalki, rivit

YTIMET = ["virta", "naiivi", "lohkottu", "lista"]
KOOT_KIB = [0.5, 1, 2, 4, 8, 16, 32, 64]


def main() -> None:
    hakemisto = Path(sys.argv[1])
    jaljet = {y: rivit(lue_jalki(hakemisto / f"{y}.txt")) for y in YTIMET}

    # @alku kayra
    koot = [int(k * 1024) // 64 for k in KOOT_KIB]  # riveinä
    print("hutiosuus (%), täysin assosiatiivinen LRU, rivi 64 B")
    print(f"{'KiB':>5}" + "".join(f"{y:>10}" for y in YTIMET))
    kayrat = {y: hutikayra(etaisyydet(r), koot) for y, r in jaljet.items()}
    for kib, koko in zip(KOOT_KIB, koot, strict=True):
        rivi = "".join(f"{100 * kayrat[y][koko] / len(jaljet[y]):10.1f}"
                       for y in YTIMET)
        print(f"{kib:>5}{rivi}")
    # @loppu kayra

    # @alku tarkistus
    # Sama tulos suoralla simuloinnilla, kun tiet == koko.
    for y, r in jaljet.items():
        for koko in (16, 128):
            if lru_hudit(r, koko, koko) != kayrat[y][koko]:
                raise SystemExit(f"{y}: pinoalgoritmi ja simulointi eroavat")
    print("pinoalgoritmi == suora simulointi: kyllä")
    # @loppu tarkistus

    # @alku konfliktit
    # Joukkoassosiatiivinen 4 KiB (64 riviä): konfliktihudit lisäävät
    # hutimäärää täysin assosiatiiviseen verrattuna.
    print("\nhudit, 4 KiB:   täysin  8-tie  2-tie  suora")
    for y, r in jaljet.items():
        maarat = [lru_hudit(r, 64, tiet) for tiet in (64, 8, 2, 1)]
        print(f"  {y:<10}" + "".join(f"{m:>7}" for m in maarat))
    # @loppu konfliktit


if __name__ == "__main__":
    main()

"""Työjoukon koko ikkunan pituuden funktiona.

Käyttö: python3 02-tyojoukko.py JÄLKIHAKEMISTO
"""

import sys
from pathlib import Path

from arkki.jalki import lue_jalki, rivit, tyojoukko

YTIMET = ["virta", "naiivi", "lohkottu", "lista"]
IKKUNAT = [64, 512, 4096]


def main() -> None:
    hakemisto = Path(sys.argv[1])
    print("työjoukko (KiB) ikkunassa, jonka pituus on viittauksina")
    print(f"{'ydin':<9}" + "".join(f"{i:>8}" for i in IKKUNAT))
    for ydin in YTIMET:
        r = rivit(lue_jalki(hakemisto / f"{ydin}.txt"))
        koot = [tyojoukko(r, i) * 64 / 1024 for i in IKKUNAT]
        print(f"{ydin:<9}" + "".join(f"{k:8.1f}" for k in koot))


if __name__ == "__main__":
    main()

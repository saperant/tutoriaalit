"""CPI-pino luvun 2 ytimille kahden tason välimuistilla.

Käyttö: python3 03-cpi-pino.py JÄLKIHAKEMISTO
"""

import sys
from pathlib import Path

from arkki.jalki import etaisyydet, hutikayra, lue_jalki, lue_laskurit, rivit
from arkki.mallit import cpi_pino

YTIMET = ["virta", "naiivi", "lohkottu", "lista"]
# @alku parametrit
PERUS_CPI = 0.5  # leveä ydin ilman muistiviivettä
SAKOT = {"L2": 12.0, "muisti": 200.0}  # jaksoa
L1_RIVEJA, L2_RIVEJA = 16, 128  # 1 KiB ja 8 KiB, kuten luvussa 3
# @loppu parametrit


def main() -> None:
    hakemisto = Path(sys.argv[1])
    laskurit = lue_laskurit(hakemisto / "laskurit.txt")
    print(f"{'ydin':<9} {'MPKI1':>6} {'MPKI2':>6} {'perus':>6} {'L2':>6}"
          f" {'muisti':>7} {'CPI':>6}")
    for ydin in YTIMET:
        # @alku pino
        r = rivit(lue_jalki(hakemisto / f"{ydin}.txt"))
        h = hutikayra(etaisyydet(r), [L1_RIVEJA, L2_RIVEJA])
        kilo = laskurit[ydin].yhteensa / 1000
        mpki = {"L2": h[L1_RIVEJA] / kilo, "muisti": h[L2_RIVEJA] / kilo}
        pino = cpi_pino(PERUS_CPI, mpki, SAKOT)
        # @loppu pino
        osat = "".join(f"{v:>7.2f}" for v in pino.values())
        print(f"{ydin:<9} {mpki['L2']:6.1f} {mpki['muisti']:6.1f}{osat}"
              f" {sum(pino.values()):6.2f}")


if __name__ == "__main__":
    main()

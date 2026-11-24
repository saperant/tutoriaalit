"""Luvun 2 ytimien energia: laskenta vai datan siirto?

Käyttö: python3 08-energia.py JÄLKIHAKEMISTO
"""

import sys
from pathlib import Path

from arkki.jalki import etaisyydet, hutikayra, lue_jalki, lue_laskurit, rivit
from arkki.teho import ENERGIA_PJ, sram_energia

YTIMET = ["virta", "naiivi", "lohkottu", "lista"]
L1_KIB, L2_KIB = 1, 8  # kuten luvussa 3
SANOJA_RIVISSA = 8  # 64 B = 8 * 64 b


def main() -> None:
    hakemisto = Path(sys.argv[1])
    laskurit = lue_laskurit(hakemisto / "laskurit.txt")
    # @alku kertoimet
    flop = (ENERGIA_PJ["liukuluku 32 b yhteenlasku"]
            + ENERGIA_PJ["liukuluku 32 b kertolasku"]) / 2
    sana = {"L1": sram_energia(L1_KIB), "L2": sram_energia(L2_KIB),
            "DRAM": ENERGIA_PJ["DRAM"]}
    # @loppu kertoimet
    print(f"{'ydin':<9} {'yht. nJ':>8} {'laskenta':>9} {'L1':>7} {'L2':>7}"
          f" {'DRAM':>7} {'pJ/FLOP':>8}")
    for ydin in YTIMET:
        # @alku energia
        r = rivit(lue_jalki(hakemisto / f"{ydin}.txt"))
        h = hutikayra(etaisyydet(r), [L1_KIB * 16, L2_KIB * 16])
        osat = {
            "laskenta": laskurit[ydin].liukuluku * flop,
            "L1": len(r) * sana["L1"],
            "L2": h[L1_KIB * 16] * SANOJA_RIVISSA * sana["L2"],
            "DRAM": h[L2_KIB * 16] * SANOJA_RIVISSA * sana["DRAM"],
        }
        yhteensa = sum(osat.values())
        # @loppu energia
        osuudet = "".join(f"{100 * e / yhteensa:{w}.1f}%"
                          for e, w in zip(osat.values(), (8, 6, 6, 6),
                                          strict=True))
        print(f"{ydin:<9} {yhteensa / 1000:8.0f} {osuudet}"
              f" {yhteensa / laskurit[ydin].liukuluku:8.1f}")


if __name__ == "__main__":
    main()

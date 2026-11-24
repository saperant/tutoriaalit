"""Usean muistitason roofline luvun 2 ytimille.

Käyttö: python3 03-roofline.py JÄLKIHAKEMISTO

Intensiteetti lasketaan kullekin tasolle sen läpi kulkevasta
liikenteestä: L1:lle kaikki viittaukset (8 B), L2:lle ja muistille
edellisen tason hudit (64 B:n rivi). Välimuistit on pienennetty
ytimien kokoon (L1 1 KiB, L2 8 KiB), jotta suhteet vastaavat
suurta kuormaa suurella koneella.
"""

import sys
from pathlib import Path

from arkki.jalki import etaisyydet, hutikayra, lue_jalki, lue_laskurit, rivit
from arkki.mallit import Taso, roofline

YTIMET = ["virta", "naiivi", "lohkottu", "lista"]
# @alku kone
HUIPPU = 32.0  # GFLOP/s
KAISTAT = {"L1": 128.0, "L2": 64.0, "muisti": 16.0}  # GB/s
L1_RIVEJA, L2_RIVEJA = 16, 128
# @loppu kone


def main() -> None:
    hakemisto = Path(sys.argv[1])
    laskurit = lue_laskurit(hakemisto / "laskurit.txt")
    print(f"huippu {HUIPPU} GFLOP/s, harjanne muistiin "
          f"{HUIPPU / KAISTAT['muisti']:.1f} FLOP/B")
    print(f"{'ydin':<9} {'I_L1':>6} {'I_L2':>6} {'I_mem':>6}"
          f" {'GFLOP/s':>8}  raja")
    for ydin in YTIMET:
        # @alku intensiteetit
        r = rivit(lue_jalki(hakemisto / f"{ydin}.txt"))
        hudit = hutikayra(etaisyydet(r), [L1_RIVEJA, L2_RIVEJA])
        flop = laskurit[ydin].liukuluku
        liikenne = {"L1": 8 * len(r), "L2": 64 * hudit[L1_RIVEJA],
                    "muisti": 64 * hudit[L2_RIVEJA]}
        tasot = [Taso(n, KAISTAT[n], flop / tavut)
                 for n, tavut in liikenne.items()]
        gflops, raja = roofline(HUIPPU, tasot)
        # @loppu intensiteetit
        i = [f"{t.intensiteetti:6.2f}" for t in tasot]
        print(f"{ydin:<9} {' '.join(i)} {gflops:8.1f}  {raja}")


if __name__ == "__main__":
    main()

"""Välimuistin koon valinta: pinta-ala, energia ja keskimääräinen
muistiviive (AMAT) neliöjuurisäännöillä."""

import math

from arkki.teho import ENERGIA_PJ, sram_ala, sram_energia

# @alku parametrit
HUTI_32K = 0.05  # hutiosuus 32 KiB:llä
DRAM_NS = 80.0
# Hutiosuus pienenee kuten koon neliöjuuri (Hartstein ym. 2006), ja
# osumaviive kasvaa johtimien mukana kuten koon neliöjuuri.


def huti(koko_kib: float) -> float:
    return HUTI_32K * math.sqrt(32 / koko_kib)


def osumaviive(koko_kib: float) -> float:
    return 1.0 * math.sqrt(koko_kib / 32)  # ns, 1 ns 32 KiB:llä
# @loppu parametrit


def main() -> None:
    print(f"{'KiB':>6} {'mm2':>7} {'huti':>6} {'osuma ns':>9}"
          f" {'AMAT ns':>8} {'pJ/viittaus':>12}")
    for koko in (8, 32, 128, 512, 2048, 8192):
        # @alku laskenta
        m = huti(koko)
        amat = osumaviive(koko) + m * DRAM_NS
        energia = sram_energia(koko) + m * 8 * ENERGIA_PJ["DRAM"]
        # @loppu laskenta
        print(f"{koko:>6} {sram_ala(koko):7.3f} {m:6.1%}"
              f" {osumaviive(koko):9.2f} {amat:8.2f} {energia:12.0f}")


if __name__ == "__main__":
    main()

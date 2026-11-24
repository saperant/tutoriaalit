"""Ensimmäinen suunnittelukysymys: kuinka suuri L1-datavälimuisti?

Suurempi välimuisti osuu useammin, mutta sen osumaviive on pidempi ja
se vie enemmän pinta-alaa. Malli on yksinkertaisin mahdollinen:
neliöjuurisääntö hutiosuudelle ja CPI-pino suoritusajalle.
"""

import math

# @alku malli
LATAUKSET = 0.25  # latausten osuus käskyistä
PERUS_CPI = 0.6  # CPI, jos jokainen lataus osuisi 2 jaksossa
L2_SAKKO = 14  # jaksoa, kun L1 ei osu
PIILOTUS = 0.7  # osuus osumaviiveen kasvusta, jonka ydin piilottaa


def cpi(koko_kib: int, osumaviive: int) -> float:
    huti = 0.05 * math.sqrt(32 / koko_kib)  # 5 % 32 KiB:llä
    lisaviive = (osumaviive - 2) * (1 - PIILOTUS)
    return PERUS_CPI + LATAUKSET * (lisaviive + huti * L2_SAKKO)
# @loppu malli


def main() -> None:
    # @alku ehdokkaat
    ehdokkaat = [(16, 2), (32, 3), (64, 4), (128, 5)]
    print(f"{'KiB':>4} {'viive':>6} {'CPI':>6} {'suht. aika':>11}"
          f" {'suht. ala':>10}")
    perus = cpi(32, 3)
    for koko, viive in ehdokkaat:
        c = cpi(koko, viive)
        print(f"{koko:>4} {viive:>6} {c:6.3f} {c / perus:11.3f}"
              f" {koko / 32:10.2f}")
    # @loppu ehdokkaat


if __name__ == "__main__":
    main()

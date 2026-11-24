"""Kierretyn parin vaimennus taajuuden funktiona.

Vaimennuksen malli on muotoa a·√f + b·f + c/√f (dB / 100 m, f MHz).
Ensimmäinen termi kuvaa virranahtoa (skin effect), toinen eristeen
häviöitä. Kertoimet ovat Cat 6 -kanavan raja-arvojen suuruusluokkaa;
tarkat raja-arvot ovat standardissa ANSI/TIA-568.
"""

import math


def vaimennus_db(f_mhz: float, pituus_m: float = 100.0) -> float:
    per_100m = (1.82 * math.sqrt(f_mhz) + 0.0169 * f_mhz
                + 0.25 / math.sqrt(f_mhz))
    return per_100m * pituus_m / 100.0


# @alku taulukko
print(" f (MHz)   100 m (dB)   jäljellä tehoa")
for f in (1, 10, 31.25, 62.5, 100, 250):
    a = vaimennus_db(f)
    print(f"{f:>8}   {a:>10.1f}   {10 ** (-a / 10):>12.2%}")
# @loppu taulukko

# @alku pituus
# Sama kaapeli puolet lyhyempänä: vaimennus desibeleinä puolittuu.
for pituus in (25, 50, 100):
    print(f"{pituus:>3} m, 100 MHz: {vaimennus_db(100, pituus):5.1f} dB")
# @loppu pituus

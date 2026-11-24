"""Desibelit: tehosuhteet, absoluuttiset tasot ja niiden laskeminen."""

import math


def db(suhde: float) -> float:
    """Tehosuhde desibeleiksi."""
    return 10 * math.log10(suhde)


def suhde(desibelit: float) -> float:
    """Desibelit tehosuhteeksi."""
    return 10 ** (desibelit / 10)


def dbm(milliwatit: float) -> float:
    """Teho milliwateista tasoksi dBm (0 dBm = 1 mW)."""
    return 10 * math.log10(milliwatit)


def mw(tasot_dbm: float) -> float:
    return 10 ** (tasot_dbm / 10)


# @alku nyrkkisaannot
for d in (3, 10, 20, 30, -3, -10):
    print(f"{d:>4} dB = {suhde(d):>8.3f} × teho")
# @loppu nyrkkisaannot

# @alku ketju
# Lähetin 20 dBm, kaapeli -6 dB, liitin -0,5 dB, vahvistin +12 dB.
taso = 20.0
for nimi, muutos in [("kaapeli", -6.0), ("liitin", -0.5),
                     ("vahvistin", 12.0)]:
    taso += muutos
    print(f"{nimi:<10} {muutos:+6.1f} dB -> {taso:5.1f} dBm"
          f" = {mw(taso):7.2f} mW")
# @loppu ketju

# Tehot eivät summaudu desibeleinä: kaksi 0 dBm:n lähdettä = 3 dBm.
print(f"0 dBm + 0 dBm = {dbm(mw(0) + mw(0)):.2f} dBm")
print(f"Jännitesuhde 2 = {20 * math.log10(2):.2f} dB")

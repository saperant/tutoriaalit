"""Numeerinen derivaatta: optimaalinen askel, Richardson ja kompleksiaskel."""

import cmath
import math
from collections.abc import Callable

f: Callable[[float], float] = math.exp      # f'(1) = e
TARKKA = math.e
EPS = 2.0**-52


# @alku kaavat
def eteen(h: float) -> float:
    return (f(1 + h) - f(1)) / h


def keski(h: float) -> float:
    return (f(1 + h) - f(1 - h)) / (2 * h)


def richardson(h: float) -> float:
    """Keskeisen erotuksen h^2-virhetermi kumotaan: (4 D(h/2) - D(h)) / 3."""
    return (4 * keski(h / 2) - keski(h)) / 3


def kompleksiaskel(h: float) -> float:
    """Im f(x + ih) / h: ei vähennyslaskua, joten ei kumoutumista."""
    return cmath.exp(1 + 1j * h).imag / h
# @loppu kaavat


# @alku paras
askeleet = [10.0**-k for k in range(1, 16)]
print("menetelmä        paras h  virhe    teoria h")
for nimi, D, teoria in [("eteenpäin", eteen, EPS ** (1 / 2)),
                        ("keskeinen", keski, EPS ** (1 / 3)),
                        ("Richardson", richardson, EPS ** (1 / 5))]:
    virhe, h = min((abs(D(h) - TARKKA), h) for h in askeleet)
    print(f"{nimi:15s}  {h:.0e}   {virhe:.0e}  {teoria:.0e}")
for h in (1e-8, 1e-100):
    virhe = abs(kompleksiaskel(h) - TARKKA) / TARKKA
    print(f"kompleksiaskel h = {h:.0e}: suhteellinen virhe <= eps: "
          f"{'kyllä' if virhe <= EPS else 'ei'}")
# @loppu paras

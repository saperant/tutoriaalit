"""Numeerinen integrointi ja jaksolliset funktiot."""

import math

import numpy as np
from numpy.typing import NDArray

Taulukko = NDArray[np.float64]


# @alku integraali
def puolisuunnikas(y: Taulukko, dx: float) -> float:
    return float(dx * (np.sum(y) - (y[0] + y[-1]) / 2))


print(" N   virhe: int_0^1 x^2   int_0^2pi e^cos(x)")
# Tarkka arvo 2 pi I0(1), missä I0(1) = sum (1/4)^k / (k!)^2 (Bessel).
I0 = sum(0.25**k / math.factorial(k) ** 2 for k in range(30))
tarkka1, tarkka2 = 1 / 3, 2 * math.pi * I0
for n in [4, 8, 16, 32]:
    x1 = np.linspace(0, 1, n + 1)
    x2 = np.linspace(0, 2 * np.pi, n + 1)
    v1 = abs(puolisuunnikas(x1**2, 1 / n) - tarkka1)
    v2 = abs(puolisuunnikas(np.exp(np.cos(x2)), 2 * np.pi / n) - tarkka2)
    jaksollinen = "< 1e-12" if v2 < 1e-12 else f"{v2:.1e}"
    print(f"{n:2d}   {v1:17.1e}   {jaksollinen:>18}")
# @loppu integraali

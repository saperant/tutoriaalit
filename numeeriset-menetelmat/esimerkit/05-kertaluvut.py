"""Integrointisääntöjen kertaluvut mitattuina: puolisuunnikas, Simpson
ja Gaussin kvadratuuri integraalille e^x välillä [0, 1]."""

import math

import numpy as np

TARKKA = math.e - 1


# @alku saannot
def puolisuunnikas(n: int) -> float:
    x = np.linspace(0.0, 1.0, n + 1)
    y = np.exp(x)
    return float((y[0] / 2 + y[1:-1].sum() + y[-1] / 2) / n)


def simpson(n: int) -> float:
    """n parillinen; painot 1, 4, 2, 4, ..., 4, 1 kertaa h/3."""
    x = np.linspace(0.0, 1.0, n + 1)
    y = np.exp(x)
    return float((y[0] + 4 * y[1:-1:2].sum() + 2 * y[2:-1:2].sum()
                  + y[-1]) / (3 * n))


def gauss(n: int) -> float:
    """n-pisteinen Gaussin-Legendren sääntö: tarkka asteen 2n-1
    polynomeille. Solmut siirretään väliltä [-1, 1] väliin [0, 1]."""
    t, w = np.polynomial.legendre.leggauss(n)
    return float(0.5 * np.sum(w * np.exp(0.5 * (t + 1))))
# @loppu saannot


def teksti(virhe: float) -> str:
    return f"{virhe:.1e}" if virhe > 1e-14 else "< 1e-14"


# @alku kertaluvut
print("  n   puolisuunnikas      Simpson")
edelliset: list[float] = []
for n in (2, 4, 8, 16, 32):
    virheet = [abs(puolisuunnikas(n) - TARKKA), abs(simpson(n) - TARKKA)]
    suhteet = ["" if not edelliset else
               f"(x{edelliset[i] / v:4.1f})" for i, v in enumerate(virheet)]
    rivi = (f"{n:3d}   {virheet[0]:.1e} {suhteet[0]:8s}"
            f" {virheet[1]:.1e} {suhteet[1]}")
    print(rivi.rstrip())
    edelliset = virheet
for n in range(1, 7):
    print(f"Gauss n={n}: virhe {teksti(abs(gauss(n) - TARKKA))}")
# @loppu kertaluvut

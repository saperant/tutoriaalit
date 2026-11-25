"""Rungen ilmiö: tasavälinen interpolointi hajoaa, Tšebyšovin ei."""

import numpy as np
import numpy.typing as npt
from scipy.interpolate import BarycentricInterpolator

Taulukko = npt.NDArray[np.float64]


def runge(x: Taulukko) -> Taulukko:
    return 1.0 / (1.0 + 25.0 * x * x)


# @alku solmut
def tasavali(n: int) -> Taulukko:
    return np.linspace(-1.0, 1.0, n + 1)


def tsebysov(n: int) -> Taulukko:
    """Tšebyšovin solmut cos((2k+1)pi / (2n+2)): tiheämpiä reunoilla."""
    k = np.arange(n + 1)
    return np.cos((2 * k + 1) * np.pi / (2 * n + 2))
# @loppu solmut


# @alku vertailu
tiheä = np.linspace(-1.0, 1.0, 2001)
print(" n  tasavali  Tsebysov")
for n in (4, 8, 16, 32):
    rivi = f"{n:2d}"
    for solmut in (tasavali, tsebysov):
        x = solmut(n)
        p = BarycentricInterpolator(x, runge(x))
        virhe = float(np.max(np.abs(p(tiheä) - runge(tiheä))))
        rivi += f"   {virhe:7.0e}"
    print(rivi)
# @loppu vertailu

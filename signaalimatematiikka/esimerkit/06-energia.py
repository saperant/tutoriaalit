"""Osasummat ja energian jakautuminen harmonisille."""

import math

import numpy as np
from numpy.typing import NDArray

Taulukko = NDArray[np.float64]

M = 16384                                      # näytteitä jaksolla
t = 2 * np.pi * (np.arange(M) + 0.5) / M       # välien keskipisteet


def kerroin(x: Taulukko, k: int) -> complex:
    """c_k = (1/2pi) int_0^2pi x(t) e^(-ikt) dt keskipistesääntönä."""
    return complex(np.mean(x * np.exp(-1j * k * t)))


kantti = np.where(t < np.pi, 1.0, -1.0)
saha = (t - np.pi) / np.pi


# @alku osasummat
def osasumma(t: Taulukko, termejä: int) -> Taulukko:
    """Kanttiaallon sarja: sum 4/(pi k) sin kt parittomilla k."""
    y = np.zeros_like(t)
    for k in range(1, 2 * termejä, 2):
        y += 4 / (np.pi * k) * np.sin(k * t)
    return y


print("termejä   keskineliövirhe   1 - (selitetty teho)")
for n in [1, 2, 5, 10, 50]:
    mse = float(np.mean((kantti - osasumma(t, n)) ** 2))
    selitetty = sum(8 / (math.pi * k) ** 2 for k in range(1, 2 * n, 2))
    print(f"{n:7d} {mse:17.4f} {1 - selitetty:22.4f}")
# @loppu osasummat

# @alku energia
kolmio = 1 - 2 * np.abs(t - np.pi) / np.pi   # jatkuva, kulmat terävät
aallot = {"kantti": kantti, "saha": saha, "kolmio": kolmio}
print("aalto     teho    osuus k=1    k<=3     k<=9   kertoimet ~")
lasku = {"kantti": "1/k", "saha": "1/k", "kolmio": "1/k^2"}
for nimi, x in aallot.items():
    teho = float(np.mean(x**2))
    osuudet = []
    for K in [1, 3, 9]:
        harm = sum(2 * abs(kerroin(x, k)) ** 2 for k in range(1, K + 1))
        osuudet.append(100 * harm / teho)
    print(f"{nimi:7s} {teho:6.4f}  {osuudet[0]:9.2f} % {osuudet[1]:6.2f} %"
          f" {osuudet[2]:6.2f} %   {lasku[nimi]}")
# @loppu energia

"""Fourier-sarjan kertoimet kantti- ja saha-aallolle."""

import math

import numpy as np
from numpy.typing import NDArray

Taulukko = NDArray[np.float64]

M = 16384                                      # näytteitä jaksolla
t = 2 * np.pi * (np.arange(M) + 0.5) / M       # välien keskipisteet


# @alku kertoimet
def kerroin(x: Taulukko, k: int) -> complex:
    """c_k = (1/2pi) int_0^2pi x(t) e^(-ikt) dt keskipistesääntönä."""
    return complex(np.mean(x * np.exp(-1j * k * t)))


kantti = np.where(t < np.pi, 1.0, -1.0)       # +1 alkupuolella, -1 lopussa
print(" k   b_k laskettu   4/(pi k)")
for k in range(1, 8):
    ck = kerroin(kantti, k)
    bk = -2 * ck.imag                         # b_k = i (c_k - c_-k)
    kaava = 4 / (math.pi * k) if k % 2 else 0.0
    print(f"{k:2d} {round(bk, 4) + 0.0:12.4f} {kaava:11.4f}")
print(f"c_0 = {round(kerroin(kantti, 0).real, 12) + 0.0}")
# @loppu kertoimet

# @alku saha
saha = (t - np.pi) / np.pi                    # nousee -1:stä 1:een
print(" k   b_k laskettu   -2/(pi k)")
for k in range(1, 6):
    bk = -2 * kerroin(saha, k).imag
    print(f"{k:2d} {bk:12.4f} {-2 / (math.pi * k):11.4f}")
# @loppu saha

"""Fourier-muunnospareja numeerisesti."""

from typing import Any

import numpy as np
from numpy.typing import NDArray

Taulukko = NDArray[np.floating[Any]]
Kompleksi = NDArray[np.complexfloating[Any, Any]]


# @alku muunnos
def muunnos(x: Kompleksi | Taulukko, t: Taulukko, dt: float,
            f: Taulukko) -> Kompleksi:
    """X(f) = int x(t) e^(-i 2 pi f t) dt summana tasavälisessä hilassa."""
    ytimet = np.exp(-2j * np.pi * np.outer(f, t))   # rivi kullekin f
    return np.asarray(ytimet @ x * dt, dtype=np.complex128)


f = np.linspace(-4, 4, 81)
N = 2000                                   # kanttipulssi [-1/2, 1/2]
dt = 1 / N
t_rect = -0.5 + (np.arange(N) + 0.5) * dt
X_rect = muunnos(np.ones(N), t_rect, dt, f)
print("rect -> sinc, max virhe < 1e-6:",
      bool(np.max(np.abs(X_rect - np.sinc(f))) < 1e-6))
for fi in [0.0, 0.5, 1.0, 1.5, 2.5]:
    i = int(np.argmin(np.abs(f - fi)))
    print(f"  X({fi:.1f}) = {round(X_rect[i].real, 4) + 0.0:+.4f}"
          f"  sinc = {round(np.sinc(fi), 4) + 0.0:+.4f}")
# @loppu muunnos

# @alku gauss
dt = 0.01
t = np.arange(-800, 801) * dt               # [-8, 8]
gauss = np.exp(-np.pi * t**2)
X_g = muunnos(gauss, t, dt, f)
print("e^(-pi t^2) -> e^(-pi f^2):",
      bool(np.max(np.abs(X_g - np.exp(-np.pi * f**2))) < 1e-12))
print("muunnos on reaalinen, koska x on parillinen:",
      bool(np.max(np.abs(X_g.imag)) < 1e-12))
# @loppu gauss

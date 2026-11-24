"""Sinimuotoinen signaali osoittimena ja osoitinsumma."""

import cmath
import math

import numpy as np
from numpy.typing import NDArray

Taulukko = NDArray[np.float64]


def kl(z: complex, d: int = 3) -> str:
    a = round(z.real, d) + 0.0
    b = round(z.imag, d) + 0.0
    merkki = "-" if b < 0 else "+"
    return f"{a:.{d}f} {merkki} {abs(b):.{d}f}i"


def napa(z: complex) -> str:
    """Osoitin muodossa A kulma phi (asteina)."""
    kulma = round(math.degrees(cmath.phase(z)), 2) + 0.0
    return f"{abs(z):.3f} kulmassa {kulma:.2f} astetta"


# @alku signaali
def kosini(A: float, f: float, phi: float, t: Taulukko) -> Taulukko:
    return A * np.cos(2 * np.pi * f * t + phi)


def osoittimesta(X: complex, f: float, t: Taulukko) -> Taulukko:
    """x(t) = Re(X e^(i 2 pi f t))."""
    return np.real(X * np.exp(2j * np.pi * f * t))


t = np.linspace(0, 0.01, 1001)
A, f, phi = 2.0, 250.0, math.pi / 3
X = cmath.rect(A, phi)
print("osoitin X =", kl(X), "=", napa(X))
ero = np.max(np.abs(kosini(A, f, phi, t) - osoittimesta(X, f, t)))
print("A cos(2 pi f t + phi) = Re(X e^(i 2 pi f t)):", bool(ero < 1e-12))
print(f"jakso T = 1/f = {1000 / f:.1f} ms, kulmataajuus = {2 * np.pi * f:.1f}"
      " rad/s")
viive = phi / (2 * np.pi * f)
print(f"vaihe pi/3 vastaa {1000 * viive:.4f} ms:n edistystä ajassa")
# @loppu signaali

# @alku summa
X1 = cmath.rect(1.0, 0.0)               # cos(2 pi f t)
X2 = cmath.rect(1.5, -math.pi / 2)      # 1.5 sin(2 pi f t)
X3 = cmath.rect(0.8, 2.5)
Xs = X1 + X2 + X3
print("summaosoitin:", kl(Xs), "=", napa(Xs))
suora = (kosini(1.0, f, 0.0, t) + 1.5 * np.sin(2 * np.pi * f * t)
         + kosini(0.8, f, 2.5, t))
print("aikatason summa = osoitinsumma:",
      bool(np.allclose(suora, osoittimesta(Xs, f, t))))
print(f"huippuarvo näytteistä {np.max(suora):.3f}, |Xs| = {abs(Xs):.3f}")
# @loppu summa

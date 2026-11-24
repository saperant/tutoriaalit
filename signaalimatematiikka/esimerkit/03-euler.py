"""Eulerin kaava numeerisesti ja trigonometriset kaavat."""

import cmath
import math

import numpy as np


def kl(z: complex, d: int = 4) -> str:
    a = round(z.real, d) + 0.0
    b = round(z.imag, d) + 0.0
    merkki = "-" if b < 0 else "+"
    return f"{a:.{d}f} {merkki} {abs(b):.{d}f}i"


# @alku tarkistus
t = np.linspace(-10, 10, 2001)
ero = np.exp(1j * t) - (np.cos(t) + 1j * np.sin(t))
print("max |e^(it) - (cos t + i sin t)| < 1e-14:",
      bool(np.max(np.abs(ero)) < 1e-14))
nolla = cmath.exp(1j * math.pi) + 1
print(f"e^(i pi) + 1 = {nolla.real:.1f} + {nolla.imag:.4e}i")
cos_e = (np.exp(1j * t) + np.exp(-1j * t)) / 2
sin_e = (np.exp(1j * t) - np.exp(-1j * t)) / 2j
print("cos ja sin eksponenteista:",
      bool(np.allclose(cos_e, np.cos(t)) and np.allclose(sin_e, np.sin(t))))
# @loppu tarkistus

# @alku identiteetit
a, b = 0.7, -1.9
# cos(a + b) = Re(e^(ia) e^(ib)), sin(a + b) = Im(e^(ia) e^(ib))
tulo = cmath.exp(1j * a) * cmath.exp(1j * b)
print(f"cos(a+b) = {math.cos(a + b):.6f}, "
      f"cos a cos b - sin a sin b = "
      f"{math.cos(a) * math.cos(b) - math.sin(a) * math.sin(b):.6f}, "
      f"Re = {tulo.real:.6f}")
# De Moivre: (cos x + i sin x)^n = cos nx + i sin nx
x, n = 0.3, 5
print("de Moivre:", kl(cmath.exp(1j * x) ** n), "=",
      kl(complex(math.cos(n * x), math.sin(n * x))))
# cos^2 x = (1 + cos 2x) / 2, koska (e^(ix) + e^(-ix))^2 / 4
print("cos^2 = (1 + cos 2x)/2:",
      bool(np.allclose(np.cos(t) ** 2, (1 + np.cos(2 * t)) / 2)))
# @loppu identiteetit

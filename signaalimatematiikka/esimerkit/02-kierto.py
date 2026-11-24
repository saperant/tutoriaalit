"""Kertolasku kompleksiluvulla on kierto ja skaalaus."""

import cmath
import math

import numpy as np


def kl(z: complex, d: int = 3) -> str:
    """Kompleksiluku pyöristettynä, ilman miinusnollia."""
    a = round(z.real, d) + 0.0
    b = round(z.imag, d) + 0.0
    merkki = "-" if b < 0 else "+"
    return f"{a:.{d}f} {merkki} {abs(b):.{d}f}i"


# @alku kierto
neliö = [1 + 1j, -1 + 1j, -1 - 1j, 1 - 1j]
kerroin = cmath.rect(2, math.pi / 6)        # skaalaus 2, kierto 30 astetta
uusi = [kerroin * p for p in neliö]
print("kerroin:", kl(kerroin))
for p, q in zip(neliö, uusi, strict=True):
    print(f"{kl(p, 1):>12} -> {kl(q):>16}  |q|/|p| = {abs(q) / abs(p):.3f}"
          f"  kulma {math.degrees(cmath.phase(q / p)):.1f}")

# Sama kuvaus 2x2-matriisina tasossa R^2.
a, b = kerroin.real, kerroin.imag
M = np.array([[a, -b], [b, a]])
for p, q in zip(neliö, uusi, strict=True):
    v = M @ np.array([p.real, p.imag])
    assert math.isclose(v[0], q.real, abs_tol=1e-12)
    assert math.isclose(v[1], q.imag, abs_tol=1e-12)
print("matriisi antaa saman tuloksen")
# @loppu kierto

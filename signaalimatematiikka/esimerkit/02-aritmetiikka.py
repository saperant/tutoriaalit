"""Kompleksilukujen laskutoimitukset ja napaesitys."""

import cmath
import math


def kl(z: complex, d: int = 3) -> str:
    """Kompleksiluku pyöristettynä, ilman miinusnollia."""
    a = round(z.real, d) + 0.0
    b = round(z.imag, d) + 0.0
    merkki = "-" if b < 0 else "+"
    return f"{a:.{d}f} {merkki} {abs(b):.{d}f}i"


# @alku perus
z = 3 + 4j
w = complex(1, -2)
print("z      =", kl(z))
print("Re, Im =", z.real, z.imag)
print("z + w  =", kl(z + w))
print("z * w  =", kl(z * w))
print("z / w  =", kl(z / w))
print("z*     =", kl(z.conjugate()))
print("|z|    =", abs(z))
print("z z*   =", kl(z * z.conjugate()))
# @loppu perus

# @alku napa
r, phi = cmath.polar(z)
print(f"r = {r:.3f}, phi = {phi:.4f} rad = {math.degrees(phi):.2f} astetta")
print("takaisin:", kl(cmath.rect(r, phi)))
for luku in [1 + 0j, 1j, -1 + 0j, -1j, complex(-1, -0.0)]:
    print(f"Im = {luku.imag:+.1f}: phase({kl(luku, 0)}) = "
          f"{cmath.phase(luku):+.4f}")
# @loppu napa

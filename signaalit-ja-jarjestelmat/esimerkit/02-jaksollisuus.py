"""Diskreetin sinin jaksollisuus ja taajuuden monikäsitteisyys."""

import math
from fractions import Fraction

import numpy as np


# @alku jakso
def jakso(taajuus: Fraction) -> int:
    """Jonon cos(2 pi f n) perusjakso, kun f = p/q on rationaalinen."""
    return taajuus.denominator


for f in (Fraction(1, 8), Fraction(3, 8), Fraction(3, 10), Fraction(5, 4)):
    N = jakso(f)
    n = np.arange(3 * N)
    x = np.cos(2 * np.pi * float(f) * n)
    toistuu = bool(np.allclose(x[:N], x[N:2 * N]))
    print(f"f = {str(f):>4} jaksoa/näyte: jakso {N:2d} näytettä,"
          f" toistuu {toistuu}")

# Kulmataajuus 1 rad/näyte: f = 1/(2 pi) on irrationaalinen.
n = np.arange(1, 100_000)
lahin = np.min(np.abs(np.cos(n) - 1.0))
print(f"cos(n): lähin paluu arvoon 1 on {lahin:.1e} päässä, ei jaksoa")
# @loppu jakso

# @alku moni
# Taajuudet f ja f + k antavat samat näytteet; f ja 1 - f samat
# kosinille.
n = np.arange(8)
for g in (0.1, 1.1, 0.9, -0.1):
    x = np.cos(2 * np.pi * g * n)
    x = np.round(x, 2) + 0.0              # ei miinusnollia
    print(f"f = {g:4}:", " ".join(f"{v:5.2f}" for v in x))
print(f"suurin erottuva taajuus 0.5 jaksoa/näyte = pi rad/näyte"
      f" ({math.pi:.4f})")
# @loppu moni

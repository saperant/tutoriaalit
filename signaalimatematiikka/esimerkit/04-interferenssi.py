"""Interferenssi ja huojunta."""

import cmath
import math

import numpy as np


# @alku interferenssi
print(" vaihe-ero  amplitudi  2|cos(d/2)|   teho (dB)")
for aste in [0, 45, 90, 120, 180]:
    d = math.radians(aste)
    summa = abs(1 + cmath.exp(1j * d))  # kaksi yksikköamplitudista aaltoa
    kaava = 2 * abs(math.cos(d / 2))
    db = 20 * math.log10(summa / 2) if summa > 1e-12 else -math.inf
    print(f"{aste:6d} {summa:12.3f} {kaava:12.3f} {db:12.2f}")
# @loppu interferenssi

# @alku huojunta
f1, f2 = 440.0, 444.0
t2 = np.linspace(0, 1, 44101)
x = np.cos(2 * np.pi * f1 * t2) + np.cos(2 * np.pi * f2 * t2)
verho = 2 * np.abs(np.cos(np.pi * (f2 - f1) * t2))
keski = np.cos(2 * np.pi * (f1 + f2) / 2 * t2)
print("summa = 2 cos(pi df t) cos(2 pi fk t):",
      bool(np.allclose(x, 2 * np.cos(np.pi * (f2 - f1) * t2) * keski)))
print("|x| <= verho:", bool(np.all(np.abs(x) <= verho + 1e-12)))
print(f"huojuntataajuus |f2 - f1| = {abs(f2 - f1):.0f} Hz, "
      f"kantoaalto {(f1 + f2) / 2:.0f} Hz")
# @loppu huojunta

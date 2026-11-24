"""Kuutiosplini: paloittainen kolmannen asteen polynomi."""

import numpy as np
from scipy.interpolate import CubicSpline

# @alku splini
tiheä = np.linspace(-1.0, 1.0, 2001)
tarkka = 1.0 / (1.0 + 25.0 * tiheä**2)
edellinen = None
print("  n   virhe     suhde")
for n in (8, 16, 32, 64, 128):
    x = np.linspace(-1.0, 1.0, n + 1)
    s = CubicSpline(x, 1.0 / (1.0 + 25.0 * x * x), bc_type="not-a-knot")
    virhe = float(np.max(np.abs(s(tiheä) - tarkka)))
    suhde = "-" if edellinen is None else f"{edellinen / virhe:.1f}"
    print(f"{n:3d}  {virhe:.1e}  {suhde:>5s}")
    edellinen = virhe
# @loppu splini

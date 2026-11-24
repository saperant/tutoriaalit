"""NumPy-taulukot: funktion arvot monessa pisteessä kerralla."""

import numpy as np
import sympy as sp

# @alku taulukko
x = np.linspace(0.0, 2.0, 5)           # 5 tasavälistä pistettä
y = x**2 - 3 * x + 2
print("x:", x)
print("y:", y)
print("nollakohdat taulukossa:", x[np.isclose(y, 0.0)])
# @loppu taulukko

# @alku lambdify
t = sp.symbols("t")
lauseke = sp.exp(-t / 2) * sp.cos(3 * t)
f = sp.lambdify(t, lauseke, modules="numpy")
tt = np.linspace(0.0, 1.0, 4)
print("f(t):", np.round(f(tt), 4))
# @loppu lambdify

# @alku vertailu
raja = 1e-12
erotus = np.max(np.abs(f(tt) - np.exp(-tt / 2) * np.cos(3 * tt)))
print("sama kuin käsin kirjoitettu:", bool(erotus < raja))
print("isclose(0.1 + 0.2, 0.3):", bool(np.isclose(0.1 + 0.2, 0.3)))
# @loppu vertailu

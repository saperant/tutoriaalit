"""Napakoordinaatit: ympyrän ala ja Gaussin integraali."""

import sympy as sp

x, y = sp.symbols("x y", real=True)
r, t, R = sp.symbols("r theta R", positive=True)

# @alku ala
# dA = dx dy = |det J| dr dtheta = r dr dtheta.
ala = sp.integrate(r, (r, 0, R), (t, 0, 2 * sp.pi))
print("ympyrän ala:", ala)
# Suorakulmaisissa koordinaateissa sama vaatii juurilausekkeen:
print("suorakulmaisesti:",
      sp.integrate(2 * sp.sqrt(R**2 - x**2), (x, -R, R)))
# @loppu ala

# @alku gauss
# I = int e^(-x^2) dx koko reaaliakselilla. I^2 on tason integraali,
# joka napakoordinaateissa on helppo: e^(-r^2) r integroituu suoraan.
I2 = sp.integrate(sp.exp(-(r**2)) * r, (r, 0, sp.oo), (t, 0, 2 * sp.pi))
print("I^2 =", I2, "=> I =", sp.sqrt(I2))
print("suoraan:", sp.integrate(sp.exp(-(x**2)), (x, -sp.oo, sp.oo)))
# @loppu gauss

"""Kaksoisintegraalit: suorakulmio, kolmio ja integrointijärjestys."""

import sympy as sp

x, y = sp.symbols("x y", real=True)

# @alku suorakulmio
# Levyn massa, kun tiheys on rho(x, y) = 1 + x y (kg/m^2) ja levy on
# [0, 2] x [0, 1] metriä. Sisempi integraali lasketaan ensin.
rho = 1 + x * y
sisempi = sp.integrate(rho, (y, 0, 1))
print("sisempi int dy =", sisempi)
print("massa =", sp.integrate(sisempi, (x, 0, 2)), "kg")
# @loppu suorakulmio

# @alku kolmio
# Kolmio 0 <= y <= x <= 1 ja integraali int int e^(x^2) dA.
# Järjestyksessä dx dy sisempi integraali on erikoisfunktio erfi,
# järjestyksessä dy dx se on helppo: e^(x^2) ei riipu y:stä.
print("sisempi dx:", sp.integrate(sp.exp(x**2), (x, y, 1)))
print("sisempi dy:", sp.integrate(sp.exp(x**2), (y, 0, x)))
hyva = sp.integrate(sp.exp(x**2), (y, 0, x), (x, 0, 1))
huono = sp.integrate(sp.exp(x**2), (x, y, 1), (y, 0, 1))
print("dy dx:", hyva, "; dx dy:", sp.simplify(huono))
print("numeerisesti:", sp.N(hyva, 8))
# @loppu kolmio

"""Epäoleelliset integraalit: ääretön väli tai rajoittamaton funktio."""

import math

import sympy as sp
from scipy import integrate

x = sp.symbols("x", positive=True)

# @alku symbolinen
for f, a, b in ((1 / x**2, 1, sp.oo), (1 / x, 1, sp.oo),
                (1 / sp.sqrt(x), 0, 1), (sp.exp(-(x**2)), 0, sp.oo)):
    print(f"int_{a}^{b} {f} dx =", sp.integrate(f, (x, a, b)))
# @loppu symbolinen

# @alku raja
# Määritelmä raja-arvona: int_1^oo = lim_{R->oo} int_1^R.
R = sp.symbols("R", positive=True)
print("int_1^R 1/x^2 dx =", sp.integrate(1 / x**2, (x, 1, R)),
      "->", sp.limit(sp.integrate(1 / x**2, (x, 1, R)), R, sp.oo))
# @loppu raja

# @alku quad
# SciPyn quad hyväksyy äärettömän rajan ja palauttaa virhearvion.
arvo, virhe = integrate.quad(lambda t: math.exp(-t * t), 0, math.inf)
print(f"quad: {arvo:.12f} (arvio virheestä {virhe:.0e}),"
      f" sqrt(pi)/2 = {math.sqrt(math.pi) / 2:.12f}")
# @loppu quad

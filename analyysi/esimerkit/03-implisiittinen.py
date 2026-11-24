"""Implisiittinen derivointi: ympyrän ja kuvan tangentit."""

import sympy as sp

x, y = sp.symbols("x y", real=True)

# @alku ympyra
# Ympyrä x^2 + y^2 = 25. Derivoidaan puolittain, y = y(x):
# 2x + 2y y' = 0, joten y' = -x/y.
F = x**2 + y**2 - 25
kulma = sp.idiff(F, y, x)
print("y' =", kulma)
print("pisteessä (3, 4): y' =", kulma.subs({x: 3, y: 4}))
tangentti = sp.expand(4 + kulma.subs({x: 3, y: 4}) * (x - 3))
print("tangentti: y =", tangentti)
# @loppu ympyra

# @alku tarkistus
# Tarkistus: ylempi puoliympyrä y = sqrt(25 - x^2) eksplisiittisesti.
ylempi = sp.sqrt(25 - x**2)
print("eksplisiittisesti y'(3) =", sp.diff(ylempi, x).subs(x, 3))
# @loppu tarkistus

# @alku kayra
# Käyrä, jota ei voi ratkaista y:n suhteen: x^3 + y^3 = 6xy
# (Descartesin lehti). Tangentin kulmakerroin pisteessä (3, 3).
lehti = x**3 + y**3 - 6 * x * y
print("lehden y' =", sp.factor(sp.idiff(lehti, y, x)))
print("pisteessä (3, 3):", sp.idiff(lehti, y, x).subs({x: 3, y: 3}))
# @loppu kayra

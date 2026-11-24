"""Yhtälöparit ja yhtälöryhmät."""

import sympy as sp

x, y, z = sp.symbols("x y z")

# @alku lineaarinen
print("pari:", sp.linsolve([2 * x + 3 * y - 7, x - y - 1], [x, y]))
print("ääretön:", sp.linsolve([x + y - 2, 2 * x + 2 * y - 4], [x, y]))
print("ei ratkaisua:", sp.linsolve([x + y - 2, x + y - 3], [x, y]))
# @loppu lineaarinen

# @alku kolme
ryhma = [x + y + z - 6, 2 * x - y + z - 3, x + 2 * y - z - 2]
print("kolme tuntematonta:", sp.linsolve(ryhma, [x, y, z]))
# @loppu kolme

# @alku epalineaarinen
# Suorakulmio: piiri 14, ala 12.
ratkaisut = sp.solve([2 * x + 2 * y - 14, x * y - 12], [x, y], dict=True)
for r in ratkaisut:
    print("sivut:", r[x], "ja", r[y])
# Ympyrä x^2 + y^2 = 25 ja suora y = x + 1
for r in sp.solve([x**2 + y**2 - 25, y - x - 1], [x, y], dict=True):
    print("leikkaus:", (r[x], r[y]))
# @loppu epalineaarinen

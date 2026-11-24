"""Ympyrä: yhtälö, keskipiste neliöksi täydentämällä ja leikkaukset."""

import sympy as sp

x, y = sp.symbols("x y", real=True)

# @alku nelio
# x^2 + y^2 - 4x + 6y - 12 = 0: täydennetään neliöiksi.
yhtalo = x**2 + y**2 - 4 * x + 6 * y - 12
muoto = (x - 2) ** 2 + (y + 3) ** 2 - 25
print("sama yhtälö:", sp.expand(muoto - yhtalo) == 0)
print("keskipiste (2, -3), säde", sp.sqrt(25))
# @loppu nelio

# @alku leikkaus
ympyra = x**2 + y**2 - 25
for b in [1, 5 * sp.sqrt(2), 8]:
    pisteet = sp.solve([ympyra, y - x - b], [x, y], dict=True)
    kuvaus = {2: "leikkaa", 1: "sivuaa", 0: "ohittaa"}[len(pisteet)]
    print(f"y = x + {b}: {kuvaus}", [(p[x], p[y]) for p in pisteet])
# @loppu leikkaus

# @alku tangentti
# Tangentti pisteessä (3, 4) on kohtisuorassa säteeseen (3, 4) nähden.
tangentti = sp.expand(3 * (x - 3) + 4 * (y - 4))
print("tangentti:", tangentti, "= 0")
print("sivuaa:", sp.solve([ympyra, tangentti], [x, y]))
# @loppu tangentti

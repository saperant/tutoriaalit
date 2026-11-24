"""Itseisarvo ja epäyhtälöiden ratkaisujoukot."""

import sympy as sp

x = sp.symbols("x", real=True)
R = sp.S.Reals

# @alku itseisarvo
print("|x - 2| = 3:", sp.solveset(sp.Abs(x - 2) - 3, x, R))
print("|x - 2| < 3:", sp.solveset(sp.Abs(x - 2) < 3, x, R))
print("|2x + 1| >= 5:", sp.solveset(sp.Abs(2 * x + 1) >= 5, x, R))
# @loppu itseisarvo

# @alku epayhtalot
print("x^2 - x - 6 > 0:", sp.solveset(x**2 - x - 6 > 0, x, R))
print("(x - 1)/(x + 2) <= 0:",
      sp.solveset((x - 1) / (x + 2) <= 0, x, R))
print("x^2 + 1 > 0:", sp.solveset(x**2 + 1 > 0, x, R))
# @loppu epayhtalot

# @alku tarkistus
# Ratkaisujoukon tarkistus testipisteillä: sisällä tosi, ulkona epätosi.
ehto = (x - 1) / (x + 2) <= 0
joukko = sp.solveset(ehto, x, R)
for piste in [-3, -2, sp.Rational(-1, 2), 1, 2]:
    if piste + 2 == 0:
        print(f"x = {piste}: nimittäjä nolla, ei määritelty")
        continue
    arvo = ehto.subs(x, piste)
    print(f"x = {piste}: ehto {arvo}, joukossa {piste in joukko}")
# @loppu tarkistus

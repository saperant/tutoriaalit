"""Integrointitekniikat: osittaisintegrointi, sijoitus, osamurrot."""

import sympy as sp

x, u = sp.symbols("x u", real=True)

# @alku osittain
# Osittaisintegrointi: int u dv = u v - int v du.
# int x e^x dx: u = x, dv = e^x dx => x e^x - int e^x dx.
kasin = x * sp.exp(x) - sp.exp(x)
print("osittain:", sp.integrate(x * sp.exp(x), x),
      "; tarkistus F' - f =", sp.simplify(sp.diff(kasin, x) - x * sp.exp(x)))
# @loppu osittain

# @alku sijoitus
# Sijoitus u = x^2, du = 2x dx: int x cos(x^2) dx = 1/2 int cos u du.
print("sijoitus:", sp.integrate(x * sp.cos(x**2), x))
print("u-muodossa:", sp.integrate(sp.cos(u) / 2, u).subs(u, x**2))
# @loppu sijoitus

# @alku osamurto
# Osamurtohajotelma ennen integrointia.
r = (3 * x + 5) / (x**2 - 2 * x - 3)
print("apart:", sp.apart(r, x))
print("integraali:", sp.integrate(r, x))
# @loppu osamurto

# @alku eialkeis
# Kaikilla alkeisfunktioilla ei ole alkeisfunktiona lausuttavaa
# integraalifunktiota: SymPy palauttaa erikoisfunktion.
for g in (sp.sin(x) / x, sp.exp(x) / x, sp.exp(-(x**2))):
    print(f"int {g} dx =", sp.integrate(g, x))
# @loppu eialkeis

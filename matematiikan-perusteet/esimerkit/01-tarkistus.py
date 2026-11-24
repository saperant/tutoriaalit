"""Käsinlaskun tarkistaminen symbolisesti SymPyllä."""

import sympy as sp

x = sp.symbols("x")

# @alku laajennus
# Käsin: (2x + 3)^2 = 4x^2 + 12x + 9
vasen = (2 * x + 3) ** 2
kasin = 4 * x**2 + 12 * x + 9
print("laajennettu:", sp.expand(vasen))
print("erotus nolla:", sp.expand(vasen - kasin) == 0)
# @loppu laajennus

# @alku virhe
# Kiireessä kirjoitettu (2x - 3)^2 = 4x^2 - 9 on väärin:
vaara = 4 * x**2 - 9
ero = sp.expand((2 * x - 3) ** 2 - vaara)
print("erotus:", ero)
print("eroaa kohdassa x = 1:", ero.subs(x, 1))
# @loppu virhe

# @alku yhtalo
# Käsin: 3x - 7 = 2(x + 1)  =>  x = 9
yhtalo = sp.Eq(3 * x - 7, 2 * (x + 1))
print("ratkaisu:", sp.solve(yhtalo, x))
print("sijoitus x = 9:", yhtalo.subs(x, 9))
# @loppu yhtalo

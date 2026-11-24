"""Polynomit ja rationaalilausekkeet."""

import sympy as sp

x = sp.symbols("x")

# @alku polynomit
p = 2 * x**3 - 3 * x**2 - 11 * x + 6
print("tekijät:", sp.factor(p))
print("juuret ja kertaluvut:", sorted(sp.roots(p, x).items()))
osamaara, jaannos = sp.div(p, x - 3, x)
print("p / (x - 3) =", osamaara, " jakojäännös", jaannos)
print("p(3) =", p.subs(x, 3), "(jäännöslause: x - 3 on tekijä)")
# @loppu polynomit

# @alku rationaali
r = (x**2 - 4) / (x**2 - 5 * x + 6)
supistettu = sp.cancel(r)
print("supistettu:", supistettu)
nimittaja = sp.denom(sp.together(r))
print("alkuperäinen ei määritelty, kun x =", sp.solve(nimittaja, x))
print("supistettu kohdassa 2:", supistettu.subs(x, 2))
print("alkuperäinen kohdassa 2:", r.subs(x, 2))
# @loppu rationaali

# @alku osamurrot
s = (5 * x + 1) / ((x - 1) * (x + 2))
print("osamurrot:", sp.apart(s, x))
print("takaisin:", sp.together(sp.apart(s, x)))
# @loppu osamurrot

"""Logaritmin laskusäännöt ja niiden ehdot."""

import sympy as sp

# @alku saannot
x, y = sp.symbols("x y")
xp, yp = sp.symbols("xp yp", positive=True)
print("ilman oletuksia:", sp.expand_log(sp.log(x * y)))
print("positiivisilla:", sp.expand_log(sp.log(xp * yp)))
print("potenssi:", sp.expand_log(sp.log(xp**3)))
print("yhdistäminen:", sp.logcombine(sp.log(xp) + 2 * sp.log(yp)))
# @loppu saannot

# @alku vastaesimerkki
# log(x*y) = log(x) + log(y) ei päde, kun x ja y ovat negatiivisia:
arvot = {x: -2, y: -3}
vasen = sp.log(x * y).subs(arvot)
oikea = (sp.log(x) + sp.log(y)).subs(arvot)
print("log((-2)(-3)) =", vasen)
print("log(-2) + log(-3) =", sp.simplify(oikea))
# @loppu vastaesimerkki

# @alku kannanvaihto
n = sp.symbols("n", positive=True)
print("log2(n) =", sp.log(n, 2))
print("log2(1024) =", sp.log(1024, 2))
print("log10(2) =", sp.N(sp.log(2, 10), 6))
# @loppu kannanvaihto

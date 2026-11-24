"""Raja-arvot SymPyllä: perustapaukset, toispuoleiset ja l'Hôpital."""

import sympy as sp

x = sp.symbols("x", real=True)
n = sp.symbols("n", positive=True, integer=True)

# @alku perus
print("sin(x)/x, x->0:", sp.limit(sp.sin(x) / x, x, 0))
print("(x^2-4)/(x-2), x->2:", sp.limit((x**2 - 4) / (x - 2), x, 2))
print("(1+1/n)^n, n->oo:", sp.limit((1 + 1 / n) ** n, n, sp.oo))
print("(3x^2+1)/(x^2-x), x->oo:",
      sp.limit((3 * x**2 + 1) / (x**2 - x), x, sp.oo))
# @loppu perus

# @alku toispuoleinen
for lauseke in (1 / x, sp.Abs(x) / x):
    vasen = sp.limit(lauseke, x, 0, "-")
    oikea = sp.limit(lauseke, x, 0, "+")
    print(f"{lauseke}: vasemmalta {vasen}, oikealta {oikea}")
# @loppu toispuoleinen

# @alku lhopital
# Muoto 0/0: osoittajan ja nimittäjän derivaattojen suhde.
osoittaja, nimittaja = sp.exp(x) - 1 - x, x**2
print("muoto:", osoittaja.subs(x, 0), "/", nimittaja.subs(x, 0))
d1o, d1n = sp.diff(osoittaja, x), sp.diff(nimittaja, x)
print("kerran:", d1o, "/", d1n, "-> muoto edelleen",
      d1o.subs(x, 0), "/", d1n.subs(x, 0))
d2o, d2n = sp.diff(osoittaja, x, 2), sp.diff(nimittaja, x, 2)
print("kahdesti:", d2o, "/", d2n, "->", d2o.subs(x, 0) / d2n.subs(x, 0))
print("limit suoraan:", sp.limit(osoittaja / nimittaja, x, 0))
# @loppu lhopital

# @alku epsilon
# Väite: 3x + 1 -> 7, kun x -> 2. Jokaiselle epsilonille kelpaa
# delta = epsilon/3, sillä |3x + 1 - 7| = 3|x - 2| < 3 delta.
eps, delta = sp.symbols("epsilon delta", positive=True)
ero = sp.Abs(3 * x + 1 - 7)
pahin = ero.subs(x, 2 + delta)            # suurin ero välin reunalla
print("reunalla ero =", pahin, "; delta = eps/3 ->",
      pahin.subs(delta, eps / 3))
# @loppu epsilon

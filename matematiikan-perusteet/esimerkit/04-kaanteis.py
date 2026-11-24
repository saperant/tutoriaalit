"""Yhdistetty funktio ja käänteisfunktio."""

import sympy as sp

x, y = sp.symbols("x y", real=True)

# @alku yhdistetty
f = 2 * x + 3
g = x**2
print("f(g(x)) =", f.subs(x, g))
print("g(f(x)) =", sp.expand(g.subs(x, f)))
# @loppu yhdistetty

# @alku kaanteis
# Celsius -> Fahrenheit ja takaisin: ratkaistaan y = F(x) x:n suhteen.
F = sp.Rational(9, 5) * x + 32
kaanteinen = sp.solve(sp.Eq(y, F), x)[0].subs(y, x)
print("F^-1(x) =", kaanteinen)
print("F(F^-1(x)) =", sp.simplify(F.subs(x, kaanteinen)))
print("F^-1(F(x)) =", sp.simplify(kaanteinen.subs(x, F)))
print("98.6 F =", kaanteinen.subs(x, sp.Rational(986, 10)), "C")
# @loppu kaanteis

# @alku rajoitus
# x^2 ei ole kääntyvä koko R:ssä: kaksi lähtöarvoa samalle tulokselle.
print("x^2 = 9:", sp.solve(sp.Eq(x**2, 9), x))
xp = sp.symbols("xp", nonnegative=True)
print("rajoitettuna x >= 0:", sp.solve(sp.Eq(xp**2, 9), xp))
# @loppu rajoitus

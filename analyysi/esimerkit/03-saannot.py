"""Derivoimissäännöt SymPyllä ja ketjusäännön tarkistus."""

import sympy as sp

x = sp.symbols("x", real=True)

# @alku perus
for f in (x**5, sp.sqrt(x), sp.exp(3 * x), sp.log(x), sp.sin(x),
          sp.tan(x), sp.atan(x)):
    print(f"d/dx {f} = {sp.simplify(sp.diff(f, x))}")
# @loppu perus

# @alku saannot
u, v = sp.Function("u")(x), sp.Function("v")(x)
print("tulo:", sp.diff(u * v, x))
print("osamäärä:", sp.simplify(sp.diff(u / v, x)))
print("yhdistetty:", sp.diff(u.subs(x, v), x))
# @loppu saannot

# @alku ketju
# Ketjusääntö käsin: d/dx sin(x^2 + 1) = cos(x^2 + 1) * 2x.
kasin = sp.cos(x**2 + 1) * 2 * x
kone = sp.diff(sp.sin(x**2 + 1), x)
print("ketjusääntö oikein:", sp.simplify(kasin - kone) == 0)
# Korkeammat derivaatat: diff(f, x, n).
print("d^4/dx^4 x^4 e^x =", sp.factor(sp.diff(x**4 * sp.exp(x), x, 4)))
# @loppu ketju

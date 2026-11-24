"""Alkuarvotehtävä Laplace-muunnoksella vaihe vaiheelta."""

import sympy as sp

t = sp.symbols("t", positive=True)
s = sp.symbols("s")
Y = sp.symbols("Y")

# @alku muunnos
# y'' + 3 y' + 2 y = 4, y(0) = 1, y'(0) = 0.
# Muunnetaan termi kerrallaan:
#   L{y''} = s^2 Y - s y(0) - y'(0),  L{y'} = s Y - y(0),  L{4} = 4/s.
y0, dy0 = 1, 0
yhtalo = sp.Eq((s**2 * Y - s * y0 - dy0) + 3 * (s * Y - y0) + 2 * Y, 4 / s)
Ys = sp.solve(yhtalo, Y)[0]
print("Y(s) =", sp.factor(Ys))
# @loppu muunnos

# @alku osamurrot
osat = sp.apart(Ys, s)
print("osamurrot:", osat)
y = sp.inverse_laplace_transform(osat, s, t)
print("y(t) =", y)
# @loppu osamurrot

# @alku tarkistus
f = sp.Function("f")
vertailu = sp.dsolve(
    f(t).diff(t, 2) + 3 * f(t).diff(t) + 2 * f(t) - 4,
    f(t),
    ics={f(0): y0, f(t).diff(t).subs(t, 0): dy0},
).rhs
print("dsolve sama:", sp.simplify(vertailu - y) == 0)
# Alku- ja loppuarvolause: y(0+) = lim s Y(s), kun s -> oo, ja
# y(oo) = lim s Y(s), kun s -> 0 (jos navat ovat vasemmassa puolitasossa).
print(
    "alkuarvo:",
    sp.limit(s * Ys, s, sp.oo),
    " loppuarvo:",
    sp.limit(s * Ys, s, 0),
)
# @loppu tarkistus

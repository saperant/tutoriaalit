"""Laplace-muunnoksen taulukko ja ominaisuudet SymPyllä."""

import sympy as sp

t = sp.symbols("t", positive=True)
s = sp.symbols("s")
a, w = sp.symbols("a omega", positive=True)


def L(f: sp.Expr) -> sp.Expr:
    return sp.laplace_transform(f, t, s, noconds=True)


# @alku taulukko
for f in (
    sp.Integer(1),
    t,
    t**2,
    sp.exp(-a * t),
    sp.sin(w * t),
    sp.cos(w * t),
    t * sp.exp(-a * t),
    sp.exp(-a * t) * sp.sin(w * t),
):
    print(f"{str(f):24s} -> {sp.simplify(L(f))}")
# @loppu taulukko

# @alku derivaatta
# Derivoinnin sääntö: L{y'} = s Y(s) - y(0). Tarkistetaan funktiolla
# y = cos(2t), jolle y(0) = 1.
y = sp.cos(2 * t)
vasen = sp.simplify(L(y.diff(t)))
oikea = sp.simplify(s * L(y) - y.subs(t, 0))
print("L{y'} =", vasen, " s Y - y(0) =", oikea)
# @loppu derivaatta

# @alku siirto
# Siirtosääntö: kertominen exp(-a t):llä siirtää muunnosta: F(s + a).
vaimeneva = sp.simplify(L(sp.exp(-a * t) * sp.cos(w * t)))
siirretty = sp.simplify(L(sp.cos(w * t)).subs(s, s + a))
print("L{exp(-a t) cos(w t)} =", vaimeneva)
print("L{cos(w t)}, s -> s + a  =", siirretty)
# @loppu siirto

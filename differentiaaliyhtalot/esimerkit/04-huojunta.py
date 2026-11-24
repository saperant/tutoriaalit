"""Vaimentamaton resonanssi ja huojunta."""

import sympy as sp

t = sp.symbols("t", nonnegative=True)
y = sp.Function("y")
alku = {y(0): 0, y(t).diff(t).subs(t, 0): 0}

# @alku resonanssi
# y'' + 4 y = cos(2 t): heräte osuu täsmälleen ominaistaajuuteen, eikä
# vaimennusta ole. Yrite A cos 2t + B sin 2t ei kelpaa, koska se ratkaisee
# homogeenisen yhtälön; yksityisratkaisussa on kerroin t.
resonanssi = sp.dsolve(
    y(t).diff(t, 2) + 4 * y(t) - sp.cos(2 * t), y(t), ics=alku
).rhs
print("w = 2:", resonanssi)
# @loppu resonanssi

# @alku huojunta
# Lähellä ominaistaajuutta (w = 1,8) amplitudi ei kasva rajatta, vaan
# vaihtelee hitaasti: kahden lähekkäisen taajuuden summa huojuu.
w = sp.Rational(9, 5)
huojunta = sp.dsolve(
    y(t).diff(t, 2) + 4 * y(t) - sp.cos(w * t), y(t), ics=alku
).rhs
print("w = 9/5:", huojunta)
tulo = sp.simplify(sp.trigsimp(sp.fu(huojunta)))
print("tulona:", tulo)
print(
    "huojunnan jakso:",
    sp.simplify(2 * sp.pi / (2 - w)),
    "=",
    round(float(2 * sp.pi / (2 - w)), 2),
    "s",
)
# @loppu huojunta

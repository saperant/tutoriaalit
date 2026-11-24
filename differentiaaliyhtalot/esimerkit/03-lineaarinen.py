"""Ensimmäisen kertaluvun lineaarinen yhtälö integroivalla tekijällä."""

import sympy as sp

t = sp.symbols("t")
y = sp.Function("y")

# @alku tekija
# y' + p(t) y = q(t). Kerrotaan integroivalla tekijällä mu = exp(int p),
# jolloin vasen puoli on (mu y)'. Esimerkki: y' + 2y = 3 exp(-t), y(0) = 0.
p = sp.Integer(2)
q = 3 * sp.exp(-t)
mu = sp.exp(sp.integrate(p, t))
print("integroiva tekijä:", mu)
C = sp.symbols("C")
yleinen = (sp.integrate(mu * q, t) + C) / mu
C0 = sp.solve(yleinen.subs(t, 0), C)[0]
kasin = sp.simplify(yleinen.subs(C, C0))
print("käsin:", kasin)
# @loppu tekija

# @alku vertailu
koneella = sp.dsolve(
    sp.Eq(y(t).diff(t) + 2 * y(t), 3 * sp.exp(-t)), y(t), ics={y(0): 0}
).rhs
print("dsolve:", koneella)
print("sama:", sp.simplify(kasin - koneella) == 0)
# @loppu vertailu

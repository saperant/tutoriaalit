"""Sekoitussäiliö: tase "muutos = sisään - ulos" yhtälöksi."""

import sympy as sp

# @alku tase
# Säiliössä on V = 200 l vettä, johon on liuennut x(t) kg suolaa.
# Sisään virtaa q = 5 l/min liuosta, jonka pitoisuus on c = 0,04 kg/l,
# ja sama määrä täysin sekoittunutta liuosta virtaa ulos.
V, q, c = 200, 5, sp.Rational(4, 100)
t = sp.symbols("t", nonnegative=True)
x = sp.Function("x")
sisaan = q * c  # kg/min
ulos = q * x(t) / V  # pitoisuus x/V kertaa virtaama
yhtalo = sp.Eq(x(t).diff(t), sisaan - ulos)
ratkaisu = sp.dsolve(yhtalo, x(t), ics={x(0): 0}).rhs
print("x(t) =", ratkaisu)
print("tasapaino:", sp.limit(ratkaisu, t, sp.oo), "kg")
# @loppu tase

# @alku aikavakio
# Aikavakio on V/q: säiliön tilavuus vaihtuu kerran tässä ajassa.
tau = sp.Rational(V, q)
print("aikavakio:", tau, "min")
for n in (1, 3, 5):
    osuus = ratkaisu.subs(t, n * tau) / sp.limit(ratkaisu, t, sp.oo)
    print(f"{n} aikavakion jälkeen {float(osuus) * 100:.1f} % tasapainosta")
# @loppu aikavakio

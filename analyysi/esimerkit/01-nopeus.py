"""Paikasta nopeus derivoimalla ja nopeudesta matka integroimalla."""

import numpy as np
import sympy as sp

# @alku symbolinen
t = sp.symbols("t", nonnegative=True)
s = 5 * t**2 - t**3 / 3          # paikka metreinä ajan t (s) funktiona
v = sp.diff(s, t)                 # nopeus: paikan derivaatta
a = sp.diff(v, t)                 # kiihtyvyys: nopeuden derivaatta
print("s(t) =", s)
print("v(t) =", v)
print("a(t) =", a)
huippu = sp.solve(sp.Eq(a, 0), t)
print("suurin nopeus hetkellä", huippu, "s, arvo", v.subs(t, huippu[0]))
# @loppu symbolinen

# @alku numeerinen
# Sama ilman symboleja: mitatut paikat 0,1 s välein.
aika = np.linspace(0.0, 10.0, 101)
paikka = 5 * aika**2 - aika**3 / 3
nopeus = np.gradient(paikka, aika)       # erotusosamäärät
print(f"numeerinen v(5) = {nopeus[50]:.4f}, tarkka", v.subs(t, 5))
# @loppu numeerinen

# @alku integraali
# Ja takaisin: nopeuden integraali on kuljettu matka.
matka = sp.integrate(v, (t, 0, 10))
print("matka 0..10 s:", matka, "=", s.subs(t, 10) - s.subs(t, 0))
# @loppu integraali

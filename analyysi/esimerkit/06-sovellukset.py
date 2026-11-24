"""Integraalin sovelluksia: ala, keskiarvo, työ, energia, todennäköisyys."""

import sympy as sp

x, t, s = sp.symbols("x t s", real=True)

# @alku ala
# Käyrien y = x ja y = x^2 väliin jäävä ala: leikkauspisteet 0 ja 1.
leikkaus = sp.solve(sp.Eq(x, x**2), x)
print("leikkauspisteet:", leikkaus,
      "; ala =", sp.integrate(x - x**2, (x, 0, 1)))
# @loppu ala

# @alku tehollisarvo
# Verkkojännite u(t) = U sin(2 pi 50 t), U = 325 V. Keskiarvo jakson
# yli on nolla; tehollisarvo (RMS) on neliöiden keskiarvon juuri.
U, f0 = 325, 50
u = U * sp.sin(2 * sp.pi * f0 * t)
jakso = sp.Rational(1, f0)
keski = sp.integrate(u, (t, 0, jakso)) / jakso
rms = sp.sqrt(sp.integrate(u**2, (t, 0, jakso)) / jakso)
print("keskiarvo", keski, "V; tehollisarvo", rms, "=",
      sp.N(rms, 4), "V")
# @loppu tehollisarvo

# @alku tyo
# Jousen venyttäminen: voima F = k s, työ W = int F ds.
k = 400                                  # N/m
W = sp.integrate(k * s, (s, 0, sp.Rational(5, 100)))
print("työ 5 cm venytykseen:", W, "J")
# Akun energia tehosta: P(t) = 20 + 5 t W tunnin ajan (t sekunteina).
E = sp.integrate(20 + 5 * t / 3600, (t, 0, 3600))
print("energia:", E, "J =", sp.N(E / 3600, 4), "Wh")
# @loppu tyo

# @alku todennakoisyys
# Tiheysfunktion integraali on todennäköisyys. Normaalijakauma N(0, 1):
phi = sp.exp(-(x**2) / 2) / sp.sqrt(2 * sp.pi)
print("int phi =", sp.integrate(phi, (x, -sp.oo, sp.oo)))
p = sp.integrate(phi, (x, -1, 1))
print("P(|X| < 1) =", p, "=", sp.N(p, 5))
# Eksponenttijakauma, keskimääräinen elinikä 1000 h: P(T > 2000 h).
lam = sp.Rational(1, 1000)
tiheys = lam * sp.exp(-lam * t)
print("P(T > 2000) =", sp.integrate(tiheys, (t, 2000, sp.oo)))
# @loppu todennakoisyys

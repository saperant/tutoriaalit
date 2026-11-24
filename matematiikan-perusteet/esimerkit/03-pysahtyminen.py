"""Sovellus: pysähtymismatka ja suurin turvallinen nopeus."""

import sympy as sp

# @alku malli
v, t_r, a, s = sp.symbols("v t_r a s", positive=True)
# Reaktiomatka v*t_r ja jarrutusmatka v^2 / (2a).
matka = v * t_r + v**2 / (2 * a)
nopeudet = sp.solve(sp.Eq(matka, s), v)
print("v(s) =", nopeudet)
# @loppu malli

# @alku arvot
arvot = {t_r: 1, a: 7, s: 50}          # 1 s, 7 m/s^2 (kuiva asfaltti), 50 m
vmax = nopeudet[0].subs(arvot)
print("tarkka:", sp.simplify(vmax), "m/s")
print("likiarvo:", round(float(vmax), 2), "m/s =",
      round(float(vmax) * 3.6, 1), "km/h")
for a_arvo, tie in [(7, "kuiva"), (3, "märkä"), (1, "jää")]:
    v_kmh = 3.6 * float(nopeudet[0].subs({t_r: 1, a: a_arvo, s: 50}))
    print(f"{tie:6s} a = {a_arvo} m/s^2: {v_kmh:5.1f} km/h")
# @loppu arvot

"""Autonomisen yhtälön tasapainot, niiden stabiilisuus ja haarautuminen."""

import sympy as sp

# @alku tasapainot
# Kalakanta kasvaa logistisesti (r = 0,5 / vuosi, K = 1000 t) ja siitä
# kalastetaan vakiomäärä h tonnia vuodessa: N' = r N (1 - N/K) - h.
n = sp.symbols("N", real=True)
r, K = sp.Rational(1, 2), 1000


def tasapainot(h: int) -> None:
    f = r * n * (1 - n / K) - h
    pisteet = sp.solve(sp.Eq(f, 0), n)
    if not pisteet:
        print(f"h = {h:3d}: ei tasapainoa, kanta romahtaa")
        return
    for p in sorted(pisteet):
        # Stabiili, jos f'(N*) < 0: pieni poikkeama palaa takaisin.
        derivaatta = f.diff(n).subs(n, p)
        if derivaatta == 0:
            laatu = "testi ei ratkaise"
        else:
            laatu = "stabiili" if derivaatta < 0 else "epästabiili"
        print(
            f"h = {h:3d}: N* = {float(p):7.2f}  f' = {float(derivaatta):+.3f}"
            f"  {laatu}"
        )


for h in (0, 60, 125, 130):
    tasapainot(h)
# @loppu tasapainot

# @alku kriittinen
# Tasapainot katoavat, kun kalastus ylittää suurimman kasvunopeuden rK/4.
print("suurin kestävä saalis rK/4 =", r * K / 4)
# @loppu kriittinen

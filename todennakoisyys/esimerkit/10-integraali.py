"""Monte Carlo -integrointi, ositettu otanta ja korkea ulottuvuus."""

import math

import numpy as np

rng = np.random.default_rng(99)
tarkka = math.sqrt(math.pi) / 2 * math.erf(1.0)   # int_0^1 exp(-x^2) dx

# @alku perus
n = 100_000
fx = np.exp(-rng.random(n) ** 2)
arvio = float(fx.mean())
keskivirhe = float(fx.std(ddof=1)) / math.sqrt(n)
print(f"Monte Carlo: {arvio:.5f} +- {keskivirhe:.5f} (tarkka {tarkka:.5f})")
# @loppu perus

# @alku ositettu
# Ositettu otanta: väli jaetaan 100 osaan, kuhunkin yhtä monta pistettä.
osia = 100
u = (np.arange(osia)[:, None] + rng.random((osia, n // osia))) / osia
fo = np.exp(-u**2)
kv = float(np.sqrt(np.sum(fo.var(axis=1, ddof=1) / fo.shape[1]))) / osia
print(f"ositettu:    {float(fo.mean()):.5f} +- {kv:.6f}")
# @loppu ositettu

# @alku ulottuvuus
# Yksikköpallon tilavuus d ulottuvuudessa: kuutiohila vaatisi 10^d
# pistettä, Monte Carlon virhe ei riipu ulottuvuudesta.
for d in (2, 5, 10):
    p = rng.uniform(-1.0, 1.0, size=(400_000, d))
    osuus = float(np.mean(np.sum(p**2, axis=1) <= 1.0))
    tarkka_v = math.pi ** (d / 2) / math.gamma(d / 2 + 1)
    print(f"d = {d:2}: tilavuus {osuus * 2**d:.4f} (tarkka {tarkka_v:.4f})")
# @loppu ulottuvuus

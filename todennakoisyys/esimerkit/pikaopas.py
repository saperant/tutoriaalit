"""Pikaoppaan idiomit: generaattori, tunnusluvut, välit ja testit."""

import math

import numpy as np

# @alku generaattori
rng = np.random.default_rng(2026)          # aina siemen ja oma olio
virrat = [np.random.default_rng(s)
          for s in np.random.SeedSequence(2026).spawn(4)]
x = rng.normal(5.0, 2.0, 10_000)
# @loppu generaattori

# @alku tunnusluvut
ka, s = float(x.mean()), float(x.std(ddof=1))     # harhaton
p50, p95, p99 = np.percentile(x, [50, 95, 99])
kv = s / math.sqrt(x.size)                         # keskivirhe
vali = (ka - 1.96 * kv, ka + 1.96 * kv)            # 95 %
# @loppu tunnusluvut

# @alku bootstrap
uudet = rng.choice(x, size=(2000, x.size))
ala, yla = np.percentile(np.median(uudet, axis=1), [2.5, 97.5])
# @loppu bootstrap

# @alku kaavat
binomi = math.comb(100, 3) * 0.02**3 * 0.98**97    # Bin(100, 0.02)
poisson = 2.0**3 * math.exp(-2.0) / math.factorial(3)
normaali_alle = 0.5 * math.erfc(-1.645 / math.sqrt(2))   # Phi(1.645)
# @loppu kaavat

# @alku regressio
y = 3.0 + 0.5 * x + rng.normal(0.0, 1.0, x.size)
r = float(np.corrcoef(x, y)[0, 1])                 # korrelaatio
b = float(np.cov(x, y)[0, 1]) / float(np.var(x, ddof=1))
a = float(y.mean()) - b * float(x.mean())          # y = a + b x
jaannos = y - (a + b * x)                          # piirrä nämä
# @loppu regressio

print(f"ka {ka:.3f}, s {s:.3f}, väli [{vali[0]:.3f}, {vali[1]:.3f}]")
print(f"p50 {float(p50):.2f}, p95 {float(p95):.2f}, p99 {float(p99):.2f}")
print(f"mediaanin väli [{float(ala):.3f}, {float(yla):.3f}],"
      f" virtoja {len(virrat)}")
print(f"Bin {binomi:.4f}, Poisson {poisson:.4f}, Phi {normaali_alle:.4f}")
print(f"r {r:.3f}, r^2 {r * r:.3f}, y = {a:.2f} + {b:.3f} x,"
      f" jäännösten hajonta {float(jaannos.std(ddof=2)):.2f}")

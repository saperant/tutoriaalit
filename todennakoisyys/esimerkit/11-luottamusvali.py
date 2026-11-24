"""Luottamusvälit: normaaliapproksimaatio, peittävyys ja bootstrap."""

import math

import numpy as np

rng = np.random.default_rng(64)

# @alku vali
# 95 %:n luottamusväli keskiarvolle: ka +- 1.96 s / sqrt(n).
mittaukset = rng.normal(12.0, 3.0, size=40)       # todellinen mu = 12
ka = float(mittaukset.mean())
kv = float(mittaukset.std(ddof=1)) / math.sqrt(mittaukset.size)
print(f"keskiarvo {ka:.2f}, 95 %:n väli [{ka - 1.96 * kv:.2f},"
      f" {ka + 1.96 * kv:.2f}]")
# @loppu vali

# @alku peittavyys
# Tulkinta: menetelmä osuu oikeaan 95 %:ssa toistoista.
toistoja, osumat = 20_000, 0
x = rng.normal(12.0, 3.0, size=(toistoja, 40))
kat = x.mean(axis=1)
kvt = x.std(axis=1, ddof=1) / math.sqrt(40)
osumat = int(np.sum(np.abs(kat - 12.0) <= 1.96 * kvt))
print(f"väli sisältää todellisen arvon {osumat / toistoja:.3f}"
      f" toistoista")
# @loppu peittavyys

# @alku bootstrap
# Mediaanin luottamusväli bootstrapilla: otos poimitaan uudelleen
# palauttaen, ja tunnusluvun hajonta luetaan uusintaotosten jakaumasta.
viiveet = rng.lognormal(mean=3.0, sigma=0.6, size=200)   # ms
uudet = rng.choice(viiveet, size=(10_000, viiveet.size), replace=True)
mediaanit = np.median(uudet, axis=1)
ala, yla = np.percentile(mediaanit, [2.5, 97.5])
print(f"mediaani {float(np.median(viiveet)):.1f} ms, bootstrap-väli"
      f" [{float(ala):.1f}, {float(yla):.1f}] ms"
      f" (todellinen {math.exp(3.0):.1f} ms)")
# @loppu bootstrap

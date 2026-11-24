"""Nopat: tarkka todennäköisyys murtolukuna ja simulaation frekvenssi."""

from collections import Counter
from fractions import Fraction
from itertools import product

import numpy as np

# @alku tarkka
# Otosavaruus: kahden nopan 36 yhtä todennäköistä tulosta.
otos = list(product(range(1, 7), repeat=2))
summat = Counter(a + b for a, b in otos)
for s in (2, 7, 12):
    print(f"P(summa = {s:2}) = {Fraction(summat[s], len(otos))}")

# Komplementti: vähintään yksi kutonen neljällä heitolla.
ei_kutosta = Fraction(5, 6) ** 4
print(f"P(vähintään yksi 6 neljällä heitolla) = 1 - (5/6)^4"
      f" = {float(1 - ei_kutosta):.4f}")
# @loppu tarkka

# @alku simulointi
rng = np.random.default_rng(2026)
for n in (100, 10_000, 1_000_000):
    heitot = rng.integers(1, 7, size=(n, 4))
    osuus = float(np.mean((heitot == 6).any(axis=1)))
    print(f"n = {n:>9,}: frekvenssi {osuus:.4f}")
# @loppu simulointi

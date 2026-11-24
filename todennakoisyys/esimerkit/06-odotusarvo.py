"""Odotusarvon lineaarisuus: kiintopisteet ja erilaiset arvot."""

import itertools
from fractions import Fraction

import numpy as np


# @alku kiintopisteet
def kiintopisteita(n: int) -> Fraction:
    """Satunnaisen permutaation kiintopisteiden odotusarvo luettelemalla."""
    perm = list(itertools.permutations(range(n)))
    summa = sum(sum(i == p[i] for i in range(n)) for p in perm)
    return Fraction(summa, len(perm))


# Lineaarisuus: E[summa] = summa E[X_i] = n * (1/n) = 1 jokaisella n.
for n in range(1, 8):
    print(f"n = {n}: E[kiintopisteet] = {kiintopisteita(n)}")
# @loppu kiintopisteet

# @alku erilaiset
# Montako eri arvoa, kun n arvontaa d:stä vaihtoehdosta?
# E = d * (1 - (1 - 1/d)^n), koska jokainen arvo on indikaattori.
d, n = 365, 100
teoria = d * (1 - (1 - 1 / d) ** n)
rng = np.random.default_rng(13)
arvot = rng.integers(0, d, size=(20_000, n))
erilaisia = np.array([len(np.unique(r)) for r in arvot])
print(f"eri syntymäpäiviä 100 hengellä: teoria {teoria:.2f},"
      f" simulointi {float(erilaisia.mean()):.2f}")
# @loppu erilaiset

"""Odotusarvo, varianssi ja keskihajonta määritelmästä ja otoksesta."""

from fractions import Fraction
from math import comb, sqrt

import numpy as np

# @alku noppa
# Nopan silmäluku: jokaisen arvon todennäköisyys on 1/6.
jakauma = {x: Fraction(1, 6) for x in range(1, 7)}
odotusarvo = sum(x * p for x, p in jakauma.items())
varianssi = sum((x - odotusarvo) ** 2 * p for x, p in jakauma.items())
print(f"E[X] = {odotusarvo} = {float(odotusarvo):.2f}")
print(f"Var(X) = {varianssi} = {float(varianssi):.3f},",
      f"keskihajonta {sqrt(varianssi):.3f}")

# Otoksen keskiarvo ja varianssi arvioivat samoja lukuja.
rng = np.random.default_rng(5)
heitot = rng.integers(1, 7, size=100_000)
print(f"100 000 heittoa: keskiarvo {float(heitot.mean()):.2f},",
      f"varianssi {float(heitot.var()):.2f}")
# @loppu noppa

# @alku binomi
# Sama määritelmä binomijakaumalle Bin(100; 0,02): summa käy läpi
# kaikki arvot 0...100. Tulos on np ja np(1 - p).
n, p = 100, 0.02
pmf = [comb(n, k) * p**k * (1 - p) ** (n - k) for k in range(n + 1)]
e = sum(k * pk for k, pk in enumerate(pmf))
v = sum((k - e) ** 2 * pk for k, pk in enumerate(pmf))
print(f"Bin(100; 0,02): E[X] = {e:.3f} (np = {n * p:.3f}),",
      f"Var(X) = {v:.3f} (np(1-p) = {n * p * (1 - p):.3f})")
# @loppu binomi

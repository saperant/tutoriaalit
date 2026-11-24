"""Binomijakauma: pakettien häviäminen."""

from math import comb

import numpy as np


# @alku pmf
def binomi(k: int, n: int, p: float) -> float:
    """P(X = k), kun X ~ Bin(n, p)."""
    return comb(n, k) * p**k * (1 - p) ** (n - k)


n, p = 100, 0.02           # 100 pakettia, kukin häviää 2 %:n todennäk.
for k in range(6):
    print(f"P(X = {k}) = {binomi(k, n, p):.4f}")
vahintaan5 = 1 - sum(binomi(k, n, p) for k in range(5))
print(f"P(X >= 5) = {vahintaan5:.4f}, odotusarvo np = {n * p:.1f}")
# @loppu pmf

# @alku simulointi
rng = np.random.default_rng(42)
havinneet = rng.binomial(n, p, size=500_000)
print(f"simulointi: P(X >= 5) = {float(np.mean(havinneet >= 5)):.4f},"
      f" keskiarvo {float(havinneet.mean()):.3f}")
# @loppu simulointi

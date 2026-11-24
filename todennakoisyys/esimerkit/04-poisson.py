"""Poisson-jakauma: pyyntöjä sekunnissa ja binomin raja-arvo."""

import math

import numpy as np


# @alku poisson
def poisson(k: int, lam: float) -> float:
    """P(X = k), kun X ~ Poisson(lam)."""
    return lam**k * math.exp(-lam) / math.factorial(k)


lam = 3.0                  # keskimäärin 3 pyyntöä sekunnissa
for k in (0, 3, 6, 9):
    print(f"P(X = {k}) = {poisson(k, lam):.4f}")
yli8 = 1 - sum(poisson(k, lam) for k in range(9))
print(f"P(X > 8) = {yli8:.5f}: noin {yli8 * 86400:.0f}"
      f" sekuntia vuorokaudessa")
# @loppu poisson

# @alku raja
# Bin(n, lam/n) lähestyy Poisson(lam):ta, kun n kasvaa.
for n in (10, 100, 10_000):
    p = lam / n
    b = math.comb(n, 3) * p**3 * (1 - p) ** (n - 3)
    print(f"n = {n:>6}: Bin P(X = 3) = {b:.4f}")
print(f"Poisson:       P(X = 3) = {poisson(3, lam):.4f}")
# @loppu raja

# @alku simulointi
rng = np.random.default_rng(9)
x = rng.poisson(lam, size=300_000)
print(f"simulointi: keskiarvo {float(x.mean()):.3f},"
      f" varianssi {float(x.var()):.3f}")
# @loppu simulointi

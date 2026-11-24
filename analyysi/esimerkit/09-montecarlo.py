"""Monte Carlo -integrointi ja sen virhe ~ 1/sqrt(N)."""

import math

import numpy as np
from scipy import integrate

# @alku pii
# Satunnaisia pisteitä neliössä [-1, 1]^2; yksikköympyrän sisään osuu
# osuus pi/4. Kiinteä siemen tekee ajosta toistettavan.
rng = np.random.default_rng(2026)
for N in (100, 10_000, 1_000_000):
    p = rng.uniform(-1.0, 1.0, size=(N, 2))
    osuu = np.count_nonzero(np.sum(p * p, axis=1) <= 1.0)
    arvio = 4 * osuu / N
    print(f"N={N:>9,}: pi ~ {arvio:.5f}, virhe {abs(arvio - math.pi):.1e},"
          f" 1/sqrt(N) = {1 / math.sqrt(N):.1e}")
# @loppu pii

# @alku vertailu
# int int_[0,1]^2 sin(x y) dA kolmella tavalla.
arvo, _ = integrate.dblquad(lambda yy, xx: math.sin(xx * yy), 0, 1, 0, 1)
p = rng.uniform(0.0, 1.0, size=(100_000, 2))
mc = float(np.mean(np.sin(p[:, 0] * p[:, 1])))
print(f"dblquad {arvo:.8f}, Monte Carlo {mc:.8f}")
# @loppu vertailu

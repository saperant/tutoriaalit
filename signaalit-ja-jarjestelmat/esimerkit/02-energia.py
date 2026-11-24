"""Energia- ja tehosignaalit numeerisesti ja kaavoista."""

import numpy as np

# @alku energia
n = np.arange(10_000)
for a in (0.5, 0.9, 0.99):
    x = a**n                              # a^n u[n], kun n >= 0
    energia = float(np.sum(x**2))
    print(f"a = {a:4}: energia {energia:9.4f},"
          f" kaava 1/(1-a^2) = {1 / (1 - a**2):9.4f}")
# @loppu energia

# @alku teho
# Teho on keskiarvo kasvavan ikkunan [-M, M] yli.
for M in (10, 100, 10_000):
    m = np.arange(-M, M + 1)
    askel = (m >= 0).astype(float)
    sini = 3.0 * np.cos(0.3 * np.pi * m)
    print(f"M = {M:6d}: teho u[n] {np.mean(askel**2):.4f},"
          f" teho 3cos {np.mean(sini**2):.4f},"
          f" energia u[n] {np.sum(askel**2):7.0f}")
# @loppu teho

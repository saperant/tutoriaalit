"""Kohinalähteiden summautuminen: riippumattomat ja korreloituneet."""

import math

import numpy as np

rng = np.random.default_rng(37)
n = 1_000_000

# @alku riippumattomat
# Riippumattomat kohinat summautuvat tehoina: sigma = sqrt(s1^2 + s2^2).
a = rng.normal(0.0, 3.0, n)
b = rng.normal(0.0, 4.0, n)
print(f"riippumattomat: hajonta {float((a + b).std()):.3f}"
      f" (teoria {math.hypot(3.0, 4.0):.3f})")
# @loppu riippumattomat

# @alku korreloituneet
# Täysin korreloituneet (sama lähde) summautuvat amplitudeina.
yhteinen = rng.normal(0.0, 1.0, n)
c = 3.0 * yhteinen
d = 4.0 * yhteinen
print(f"korreloituneet: hajonta {float((c + d).std()):.3f} (teoria 7.000)")
# Erotus kumoaa yhteisen kohinan: differentiaalinen mittaus.
print(f"differentiaalinen (c - 0.75 d): hajonta"
      f" {float((c - 0.75 * d).std()):.3f}")
# @loppu korreloituneet

# @alku kovarianssi
# Yleisesti Var(X + Y) = Var X + Var Y + 2 Cov(X, Y).
x = rng.normal(0.0, 1.0, n)
y = 0.6 * x + 0.8 * rng.normal(0.0, 1.0, n)     # korrelaatio 0.6
kov = float(np.cov(x, y)[0, 1])
print(f"korrelaatio {float(np.corrcoef(x, y)[0, 1]):.3f},"
      f" Var(x + y) = {float((x + y).var()):.3f},"
      f" kaava {float(x.var() + y.var()) + 2 * kov:.3f}")
# @loppu kovarianssi

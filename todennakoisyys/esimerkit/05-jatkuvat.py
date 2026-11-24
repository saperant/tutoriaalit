"""Jatkuvat jakaumat: tasainen, eksponentti ja normaali."""

import math

import numpy as np

rng = np.random.default_rng(21)
n = 1_000_000

# @alku tasainen
u = rng.uniform(2.0, 5.0, n)
print(f"Tas(2, 5): keskiarvo {float(u.mean()):.3f} (teoria 3.500),"
      f" varianssi {float(u.var()):.3f} (teoria {3**2 / 12:.3f})")
# @loppu tasainen

# @alku eksponentti
# Pyyntöjen väliajat, kun pyyntöjä tulee 3 sekunnissa: Exp(3).
lam = 3.0
valit = rng.exponential(1 / lam, n)
print(f"Exp(3): keskiarvo {float(valit.mean()):.4f} s (teoria"
      f" {1 / lam:.4f}), P(T > 1 s) = {float(np.mean(valit > 1)):.4f}"
      f" (teoria {math.exp(-lam):.4f})")
# Muistittomuus: odotettu jäljellä oleva aika ei riipu odotetusta.
jatko = valit[valit > 0.5] - 0.5
print(f"jo 0.5 s odotettu: jäljellä keskimäärin {float(jatko.mean()):.4f} s")
# @loppu eksponentti

# @alku normaali
x = rng.normal(10.0, 2.0, n)
for k in (1, 2, 3):
    osuus = float(np.mean(np.abs(x - 10.0) < k * 2.0))
    teoria = math.erf(k / math.sqrt(2))
    print(f"P(|X - mu| < {k} sigma) = {osuus:.4f} (teoria {teoria:.4f})")
# @loppu normaali

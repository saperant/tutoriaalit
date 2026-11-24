"""Radiotie: vapaan tilan vaimennus ja monitie-eteneminen."""

import math

import numpy as np


def fspl_db(etaisyys_m: float, taajuus_hz: float) -> float:
    """Vapaan tilan vaimennus (Friis): 20·log10(4πd/λ)."""
    aallonpituus = 3e8 / taajuus_hz
    return 20 * math.log10(4 * math.pi * etaisyys_m / aallonpituus)


# @alku fspl
print("  d (m)   2,4 GHz   5,5 GHz")
for d in (1, 10, 100, 1000):
    print(f"{d:>7} {fspl_db(d, 2.4e9):>8.1f} {fspl_db(d, 5.5e9):>9.1f}")
# @loppu fspl

# @alku rayleigh
# Monitie: monen heijastuksen summa on kompleksinen normaalijakautunut
# kerroin, jonka tehon jakauma on eksponentiaalinen (Rayleigh-häipymä).
rng = np.random.default_rng(1)
n = 200_000
h = (rng.standard_normal(n) + 1j * rng.standard_normal(n)) / math.sqrt(2)
teho = np.abs(h) ** 2
for haipyma_db in (-10, -20):
    raja = 10 ** (haipyma_db / 10)
    simuloitu = float(np.mean(teho < raja))
    teoria = 1 - math.exp(-raja)
    print(f"teho alle {haipyma_db} dB: simuloitu {simuloitu:.3f},"
          f" teoria {teoria:.3f}")
# @loppu rayleigh

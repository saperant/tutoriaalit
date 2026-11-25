"""Otoskoko ja testin voima: kuinka monta käyttäjää A/B-testi tarvitsee."""

import math
from statistics import NormalDist

import numpy as np

# @alku otoskoko
# Halutaan havaita konversion nousu 10 %:sta 11 %:iin, kun
# merkitsevyystaso on 5 % (kaksisuuntainen) ja voima 80 %.
p1, p2 = 0.10, 0.11
alfa, voima = 0.05, 0.80
z_alfa = NormalDist().inv_cdf(1 - alfa / 2)          # 1,96
z_beta = NormalDist().inv_cdf(voima)                 # 0,84
p = (p1 + p2) / 2
n = math.ceil((z_alfa * math.sqrt(2 * p * (1 - p))
               + z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
              / (p2 - p1) ** 2)
print(f"käyttäjiä tarvitaan {n} ryhmää kohti")
# @loppu otoskoko


# @alku simulointi
def loydosten_osuus(n: int, pa: float, pb: float, toistoja: int,
                    rng: np.random.Generator) -> float:
    """Kuinka usein kahden osuuden z-testi antaa p < 0,05."""
    ka = rng.binomial(n, pa, toistoja)
    kb = rng.binomial(n, pb, toistoja)
    yhd = (ka + kb) / (2 * n)
    z = (kb - ka) / n / np.sqrt(yhd * (1 - yhd) * 2 / n)
    return float(np.mean(np.abs(z) > z_alfa))


rng = np.random.default_rng(808)
print(f"voima otoskoolla {n}:",
      f"{loydosten_osuus(n, p1, p2, 20_000, rng):.3f}")
print("voima otoskoolla 2000:",
      f"{loydosten_osuus(2000, p1, p2, 20_000, rng):.3f}")
print("väärät löydökset, kun eroa ei ole:",
      f"{loydosten_osuus(n, p1, p1, 20_000, rng):.3f}")
# @loppu simulointi

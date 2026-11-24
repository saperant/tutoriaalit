"""Syntymäpäiväongelma ja tunnisteiden törmäykset."""

import math

import numpy as np


# @alku tarkka
def tormays(n: int, d: int) -> float:
    """P(ainakin kaksi n:stä saa saman arvon d vaihtoehdosta)."""
    ei_tormaysta = 1.0
    for i in range(n):
        ei_tormaysta *= (d - i) / d
    return 1.0 - ei_tormaysta


for n in (10, 23, 50):
    print(f"{n:2} henkilöä: P(sama syntymäpäivä) = {tormays(n, 365):.3f}")
# @loppu tarkka

# @alku simulointi
rng = np.random.default_rng(7)
kokeita = 20_000
paivat = rng.integers(0, 365, size=(kokeita, 23))
jarjestetty = np.sort(paivat, axis=1)
sama = (np.diff(jarjestetty, axis=1) == 0).any(axis=1)
print(f"simulointi, 23 henkilöä: {float(sama.mean()):.3f}")
# @loppu simulointi

# @alku tunnisteet
# Satunnaiset 32-bittiset tunnisteet: montako ennen 50 %:n
# törmäysriskiä? Likiarvo n = sqrt(2 d ln 2).
d = 2**32
n50 = math.sqrt(2 * d * math.log(2))
print(f"32-bittiset tunnisteet: 50 % törmäysriski noin {n50:,.0f}"
      f" tunnisteen kohdalla")
print(f"128-bittiset: noin {math.sqrt(2 * 2**128 * math.log(2)):.1e}")
# @loppu tunnisteet

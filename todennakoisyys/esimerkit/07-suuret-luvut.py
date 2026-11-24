"""Suurten lukujen laki: keskiarvo lähestyy odotusarvoa."""

import numpy as np

# @alku keskiarvo
rng = np.random.default_rng(1)
heitot = rng.integers(1, 7, size=1_000_000)
kumulatiivinen = np.cumsum(heitot) / np.arange(1, heitot.size + 1)
for n in (10, 100, 1_000, 10_000, 100_000, 1_000_000):
    ka = float(kumulatiivinen[n - 1])
    print(f"n = {n:>9,}: keskiarvo {ka:.4f}, virhe {abs(ka - 3.5):.4f}")
# @loppu keskiarvo

# @alku cauchy
# Ilman äärellistä odotusarvoa laki ei päde: Cauchyn jakauman
# keskiarvo ei asetu, vaikka otosta kasvatetaan.
c = rng.standard_cauchy(1_000_000)
ck = np.cumsum(c) / np.arange(1, c.size + 1)
print("Cauchy:", " ".join(f"{float(ck[n - 1]):7.2f}"
                          for n in (100, 10_000, 1_000_000)))
# @loppu cauchy

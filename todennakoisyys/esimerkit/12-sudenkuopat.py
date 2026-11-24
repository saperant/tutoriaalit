"""A/B-testauksen sudenkuopat: kurkkiminen ja monivertailu."""

import math

import numpy as np
import numpy.typing as npt

rng = np.random.default_rng(88)


# @alku apu
def p_arvo(a: npt.NDArray[np.bool_], b: npt.NDArray[np.bool_]) -> float:
    """Kahden osuuden z-testin kaksisuuntainen p-arvo."""
    pa, pb = float(a.mean()), float(b.mean())
    p = (float(a.sum()) + float(b.sum())) / (a.size + b.size)
    kv = math.sqrt(p * (1 - p) * (1 / a.size + 1 / b.size))
    return math.erfc(abs(pb - pa) / kv / math.sqrt(2)) if kv > 0 else 1.0
# @loppu apu


# @alku kurkkiminen
# A/A-testi: versiot ovat samat (konversio 10 %). Jos testi lopetetaan
# heti, kun p < 0.05 jossakin 20 välitarkistuksessa, väärä löydös on
# paljon yleisempi kuin 5 %.
kokeita, n, tarkistuksia = 2000, 4000, 20
kerran = kurkkien = 0
for _ in range(kokeita):
    a = rng.random(n) < 0.10
    b = rng.random(n) < 0.10
    kerran += p_arvo(a, b) < 0.05
    rajat = np.linspace(n // tarkistuksia, n, tarkistuksia).astype(int)
    kurkkien += any(p_arvo(a[:m], b[:m]) < 0.05 for m in rajat)
print(f"väärä löydös, yksi analyysi: {kerran / kokeita:.3f}")
print(f"väärä löydös, kurkkien 20 kertaa: {kurkkien / kokeita:.3f}")
# @loppu kurkkiminen

# @alku monivertailu
# 20 riippumatonta mittaria ilman todellista eroa: todennäköisyys, että
# ainakin yksi on "merkitsevä", on 1 - 0.95^20.
print(f"ainakin yksi 20 mittarista p < 0.05: {1 - 0.95**20:.3f};"
      f" Bonferroni-raja 0.05/20 = {0.05 / 20:.4f}")
# @loppu monivertailu

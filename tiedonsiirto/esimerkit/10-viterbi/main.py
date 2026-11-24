"""Konvoluutiokoodin BER AWGN-kanavassa ja purskevirheet lomituksella."""

import numpy as np
from konvoluutio import koodaa, lomita, purkulomitus, viterbi
from scipy.special import erfc

rng = np.random.default_rng(17)
B, L = 200, 502                               # 200 lohkoa, 502 bittiä

# @alku ber
print("Eb/N0   koodaamaton   kova       pehmeä")
for EbN0_dB in (2.0, 3.0, 4.0, 5.0):
    EbN0 = 10 ** (EbN0_dB / 10)
    u = rng.integers(0, 2, (B, L))
    c = koodaa(u)
    R = L / c.shape[1]                        # 502 / 1008
    y = (1.0 - 2 * c) + np.sqrt(1 / (2 * R * EbN0)) * rng.standard_normal(
        c.shape)
    kova = np.mean(viterbi(y, pehmea=False) != u)
    pehmea = np.mean(viterbi(y, pehmea=True) != u)
    print(f"{EbN0_dB:4.0f} dB   {0.5 * erfc(np.sqrt(EbN0)):9.2e}"
          f"  {kova:9.2e}  {pehmea:9.2e}")
# @loppu ber

# @alku purske
# Kanava, jossa jokaisessa lohkossa on yksi 12 bitin purske (tuhoutuneet
# näytteet ovat nollia) ja muuten hyvä signaali-kohinasuhde.
u = rng.integers(0, 2, (B, L))
c = koodaa(u)
for nimi, rivit in (("ilman lomitusta", 1), ("lomitus 4 riviä", 4),
                    ("lomitus 12 riviä", 12)):
    x = 1.0 - 2 * lomita(c, rivit)
    alut = rng.integers(0, x.shape[1] - 12, B)
    for b, a in enumerate(alut):
        x[b, a: a + 12] = 0.0                 # häipymä: ei tietoa
    y = purkulomitus(x + 0.3 * rng.standard_normal(x.shape), rivit)
    virheelliset = np.mean(np.any(viterbi(y, pehmea=True) != u, axis=1))
    print(f"{nimi:17s}: virheellisiä lohkoja {100 * virheelliset:5.1f} %")
# @loppu purske

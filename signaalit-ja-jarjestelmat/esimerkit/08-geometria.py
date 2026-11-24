"""Taajuusvaste napojen ja nollien etäisyyksistä yksikköympyrällä."""

import numpy as np
from scipy import signal

# @alku geometria
nollat = np.array([np.exp(0.6j), np.exp(-0.6j)])      # yksikköympyrällä
navat = np.array([0.9 * np.exp(1.2j), 0.9 * np.exp(-1.2j)])
k = 1.0
b, a = signal.zpk2tf(nollat, navat, k)

w = np.array([0.0, 0.6, 1.2, 2.0, np.pi])             # rad/näyte
_, H = signal.freqz(b, a, worN=w)
for wi, Hi in zip(w, H, strict=True):
    z = np.exp(1j * wi)
    etaisyydet = np.prod(np.abs(z - nollat)) / np.prod(np.abs(z - navat))
    print(f"w = {wi:5.3f}: |H| freqz {abs(Hi):8.4f},"
          f" etäisyyksistä {k * etaisyydet:8.4f}")
# @loppu geometria

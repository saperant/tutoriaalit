"""Liukuva keskiarvo konvoluutiona."""

import numpy as np


# @alku keskiarvo
rng = np.random.default_rng(2026)
n = np.arange(20000)
puhdas = np.sin(2 * np.pi * n / 200)               # hidas signaali
kohina = rng.uniform(-1.0, 1.0, size=n.size)       # keskihajonta 1/sqrt 3
mitattu = puhdas + kohina
print(" M   kohinan hajonta   1/sqrt(3M)   signaalin vaimennus")
for M in [1, 4, 16, 64]:
    ikkuna = np.ones(M) / M
    jäljelle = np.convolve(kohina, ikkuna, mode="valid")
    suodatettu = np.convolve(puhdas, ikkuna, mode="valid")
    vahvistus = np.max(np.abs(suodatettu)) / np.max(np.abs(puhdas))
    print(f"{M:2d} {np.std(jäljelle):14.2f} {1 / np.sqrt(3 * M):13.2f}"
          f" {vahvistus:17.2f}")
# @loppu keskiarvo

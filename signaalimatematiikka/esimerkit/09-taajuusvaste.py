"""Liukuvan keskiarvon taajuusvaste."""

import numpy as np


# @alku taajuusvaste
M, N = 8, 512
ikkuna = np.ones(M) / M
H = np.fft.rfft(ikkuna, n=N)                   # nollilla täytetty
f = np.fft.rfftfreq(N)                         # jaksoina näytettä kohti
with np.errstate(invalid="ignore", divide="ignore"):
    kaava = np.abs(np.sin(np.pi * f * M) / (M * np.sin(np.pi * f)))
kaava[0] = 1.0
print("|H| = |sin(pi f M) / (M sin(pi f))|:",
      bool(np.allclose(np.abs(H), kaava)))
for fi in [0.0, 1 / 16, 1 / 8, 3 / 16, 0.25, 0.5]:
    i = int(round(fi * N))
    print(f"  f = {fi:.4f}: |H| = {round(abs(H[i]), 4) + 0.0:.4f}")
# @loppu taajuusvaste

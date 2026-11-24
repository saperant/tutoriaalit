"""Konvoluutio matriisitulona: Toeplitz-matriisi ja dekonvoluutio."""

import numpy as np
from scipy import linalg

# @alku toeplitz
h = np.array([1.0, 0.5, 0.25])
N = 6
sarake = np.concatenate([h, np.zeros(N - 1)])        # pituus N + len(h) - 1
H = linalg.toeplitz(sarake, np.zeros(N))
print("H =")
for rivi in H:
    print("  ", " ".join(f"{v:4.2f}" for v in rivi))
x = np.array([1.0, 2.0, 3.0, 0.0, -1.0, 2.0])
print("H @ x == convolve:", bool(np.allclose(H @ x, np.convolve(x, h))))
# @loppu toeplitz

# @alku dekonvoluutio
# Tunnettu kanava, tuntematon syöte: ratkaistaan pienimmän neliösumman
# tehtävä H x = y. Kohinaa lisätään, jotta tilanne on realistinen.
rng = np.random.default_rng(3)
y = np.convolve(x, h) + 0.01 * rng.normal(size=N + len(h) - 1)
arvio, *_ = linalg.lstsq(H, y)
arvio = np.round(arvio, 2) + 0.0
print("palautettu x:", " ".join(f"{v:5.2f}" for v in arvio))
print(f"kuntoluku {np.linalg.cond(H):.2f}")
# @loppu dekonvoluutio

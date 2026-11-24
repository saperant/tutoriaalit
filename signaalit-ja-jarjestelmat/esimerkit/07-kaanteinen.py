"""Käänteinen Z-muunnos osamurtoluvuilla (scipy.signal.residuez)."""

import numpy as np
from scipy import signal

# @alku osamurrot
# H(z) = 1 / ((1 - 0.5 z^-1)(1 + 0.25 z^-1))
b = np.array([1.0])
a = np.convolve([1.0, -0.5], [1.0, 0.25])     # polynomien kertolasku
r, p, k = signal.residuez(b, a)
for ri, pi in zip(r, p, strict=True):
    print(f"termi {ri.real:+.4f} / (1 - ({pi.real:+.4f}) z^-1)")

n = np.arange(10)
kaava = sum(ri.real * pi.real**n for ri, pi in zip(r, p, strict=True))
h = signal.lfilter(b, a, np.r_[1.0, np.zeros(9)])
print("h[n] =", " ".join(f"{v:.4f}" for v in h[:6]))
print("kaava == lfilter:", bool(np.allclose(kaava, h)))
# @loppu osamurrot

# @alku kaskadi
# Sarjaankytkentä: siirtofunktiot kerrotaan, eli kertoimet konvoloidaan.
b1, a1 = [1.0, 1.0], [1.0, -0.5]
b2, a2 = [1.0, -1.0], [1.0, 0.25]
x = np.random.default_rng(8).normal(size=100)
perakkain = signal.lfilter(b2, a2, signal.lfilter(b1, a1, x))
yhdessa = signal.lfilter(np.convolve(b1, b2), np.convolve(a1, a2), x)
print("sarjaan == tulo:", bool(np.allclose(perakkain, yhdessa)))
# @loppu kaskadi

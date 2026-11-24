"""Pikaoppaan SciPy-reseptit: suunnittelu, tarkistus ja monitaajuus."""

import numpy as np
from scipy import signal

fs = 48_000.0
x = np.random.default_rng(0).standard_normal(48_000)

# @alku fir
lkm, beta = signal.kaiserord(80.0, 1_000.0 / (fs / 2))     # A, siirtyma
h = signal.firwin(lkm | 1, 5_000.0, window=("kaiser", beta), fs=fs)
h_pm = signal.remez(101, [0, 4_500, 5_500, fs / 2], [1, 0],
                    weight=[1, 10], fs=fs)
h_vapaa = signal.firwin2(255, [0, 1e3, 2e3, fs / 2], [1, 1, 2, 2],
                         fs=fs)
# @loppu fir

# @alku iir
n, raja = signal.ellipord(5_000, 6_000, 0.1, 80, fs=fs)
sos = signal.ellip(n, 0.1, 80, raja, output="sos", fs=fs)
y = signal.sosfilt(sos, x)                       # aina sos, ei (b, a)
zi = signal.sosfilt_zi(sos) * x[0]               # alkutila vakaalle
# @loppu iir

# @alku tarkista
f, H = signal.sosfreqz(sos, worN=1 << 15, fs=fs)
db = 20 * np.log10(np.maximum(np.abs(H), 1e-15))
aaltoilu = np.ptp(db[f <= 5_000])
vaimennus = -db[f >= 6_000].max()
# @loppu tarkista

# @alku monitaajuus
y4 = signal.resample_poly(x, 1, 4)               # desimointi 4
y48 = signal.resample_poly(x[:44_100], 160, 147)  # 44,1 -> 48 kHz
yu = signal.upfirdn(h, x, up=2, down=3)          # oma suodin
# @loppu monitaajuus

print(f"FIR {lkm | 1} kerrointa, IIR aste {n}")
print(f"aaltoilu {aaltoilu:.3f} dB, vaimennus {vaimennus:.1f} dB")
print(f"pituudet {y4.size}, {y48.size}, {yu.size}, {h_pm.size},"
      f" {h_vapaa.size}, {zi.shape}")

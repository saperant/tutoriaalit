"""Kohinan tehospektri: periodogrammi vs. Welchin menetelmä."""

import numpy as np
from scipy import signal

# @alku welch
rng = np.random.default_rng(12)
fs = 1_000.0
sigma = 0.1
x = sigma * rng.normal(size=100_000)
x += 0.05 * np.sin(2 * np.pi * 125 * np.arange(len(x)) / fs)
teoria = sigma**2 / (fs / 2)                  # yksipuolinen PSD, V^2/Hz

f1, P1 = signal.periodogram(x, fs=fs)
f2, P2 = signal.welch(x, fs=fs, nperseg=1_024)
for nimi, f, P in (("periodogrammi", f1, P1), ("welch 1024", f2, P2)):
    kohina = P[(f > 200) & (f < 400)]
    hajonta = np.std(kohina) / np.mean(kohina)
    huippu = f[np.argmax(P)]
    print(f"{nimi:<13} taso {np.mean(kohina) / teoria:5.3f} x teoria,"
          f" hajonta {hajonta:5.3f}, huippu {huippu:5.1f} Hz")
print(f"teoria {teoria:.1e} V^2/Hz, Welchin taajuusväli {f2[1]:.3f} Hz")
# @loppu welch

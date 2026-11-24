"""Ikkunafunktioiden pääkeilan leveys, sivukeilat ja vahvistus."""

import numpy as np
from scipy import signal

# @alku ikkunat
N = 64
TIHEYS = 64                                   # nollilla täyttö: tiheä hila
print(f"{'ikkuna':<10} {'keila/välit':>11} {'sivukeila/dB':>12}"
      f" {'vahvistus':>9}")
for nimi in ("boxcar", "hann", "hamming", "blackman"):
    w = signal.get_window(nimi, N, fftbins=True)
    W = np.abs(np.fft.rfft(w, n=N * TIHEYS))
    W_db = 20 * np.log10(np.maximum(W / W[0], 1e-12))
    ensimmainen_minimi = int(np.argmax(np.diff(W_db) > 0))
    leveys = 2 * ensimmainen_minimi / TIHEYS      # nollasta nollaan
    sivukeila = float(np.max(W_db[ensimmainen_minimi:]))
    vahvistus = float(np.mean(w))                 # koherentti vahvistus
    print(f"{nimi:<10} {leveys:11.2f} {sivukeila:12.1f} {vahvistus:9.3f}")
# @loppu ikkunat

# @alku heikko
# Vahva 100 Hz ja 60 dB heikompi 160 Hz, epäkokonainen määrä jaksoja.
fs, N = 1_000.0, 256
t = np.arange(N) / fs
x = np.cos(2 * np.pi * 100.7 * t) + 1e-3 * np.cos(2 * np.pi * 160.3 * t)
f = np.fft.rfftfreq(N, d=1 / fs)
for nimi in ("boxcar", "hann", "blackman"):
    w = signal.get_window(nimi, N)
    X = np.abs(np.fft.rfft(x * w)) / np.sum(w) * 2
    lahella = (f > 150) & (f < 170)
    taso = 20 * np.log10(np.max(X[lahella]))
    tausta = 20 * np.log10(np.median(X[(f > 130) & (f < 150)]))
    print(f"{nimi:<9} taso 160 Hz:n kohdalla {taso:6.1f} dB,"
          f" tausta 130..150 Hz {tausta:6.1f} dB")
# @loppu heikko

"""Amplitudin arvio ikkunoidusta spektristä ja nollilla täytön vaikutus."""

import numpy as np
from scipy import signal

# @alku amplitudi
fs, N = 1_000.0, 200
t = np.arange(N) / fs
x = 2.5 * np.cos(2 * np.pi * 123.4 * t)
w = signal.get_window("hann", N)
for taytto in (N, 4 * N, 32 * N):
    X = np.fft.rfft(x * w, n=taytto)
    f = np.fft.rfftfreq(taytto, d=1 / fs)
    k = int(np.argmax(np.abs(X)))
    A = 2 * abs(X[k]) / np.sum(w)            # ikkunan vahvistus korjattu
    print(f"pituus {taytto:5d}: huippu {f[k]:7.2f} Hz, amplitudi {A:.3f}")
# @loppu amplitudi

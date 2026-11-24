"""Toisen asteen resonaattori: värähtelevä ja vaimeneva impulssivaste."""

import numpy as np
from scipy import signal

# @alku resonaattori
fs = 8_000.0
f0 = 440.0                               # resonanssitaajuus
for r in (0.99, 0.999, 1.0, 1.001):
    theta = 2 * np.pi * f0 / fs
    a = [1.0, -2 * r * np.cos(theta), r**2]
    d = np.zeros(8_000)
    d[0] = 1.0
    h = signal.lfilter([1.0], a, d)
    # Jakso nollanylityksistä, verhokäyrä huipuista.
    nousevat = np.flatnonzero((h[:-1] < 0) & (h[1:] >= 0))
    jakso = float(np.mean(np.diff(nousevat)))
    alku = float(np.max(np.abs(h[:200])))
    loppu = float(np.max(np.abs(h[-200:])))
    print(f"r = {r:5}: taajuus {fs / jakso:6.1f} Hz,"
          f" |h| alussa {alku:8.2f}, lopussa {loppu:9.2e}")
# @loppu resonaattori

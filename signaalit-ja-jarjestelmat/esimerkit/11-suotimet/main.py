"""Suodinkirjaston käyttö: hurinan poisto ja tasoitus lohkoittain."""

import numpy as np
from scipy import signal

from suotimet import Eksponentiaalinen, lovi, vahvistus_db

fs = 500.0
b, a = lovi(50.0, fs)
for f in (0.0, 45.0, 50.0, 100.0):
    db = round(max(vahvistus_db(b, a, f, fs), -120.0), 1) + 0.0
    print(f"lovi {f:5.1f} Hz: {db:7.1f} dB")

t = np.arange(2_000) / fs
x = 1.0 + 0.3 * np.sin(2 * np.pi * 50 * t)
y = signal.lfilter(b, a, x)
ema = Eksponentiaalinen(0.05)
tasattu = np.concatenate([ema.kasittele(y[i:i + 250])
                          for i in range(0, len(y), 250)])
print(f"lopussa: lovi {y[-1]:.4f}, tasattu {tasattu[-1]:.4f}")

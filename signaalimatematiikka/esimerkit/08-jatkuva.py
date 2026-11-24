"""Jatkuva konvoluutio: rect * rect on kolmio, ja sen muunnos on sinc^2."""

import numpy as np

# @alku kolmio
dt = 0.001
k = np.arange(-1000, 1001)                         # t = k dt, [-1, 1]
t = k * dt
# Reunapisteet puolella painolla, jotta pulssin pinta-ala on 1.
rect = np.where(np.abs(k) < 500, 1.0, np.where(np.abs(k) == 500, 0.5, 0.0))
kolmio = np.convolve(rect, rect, mode="same") * dt  # int r(s) r(t - s) ds
tarkka = np.maximum(0.0, 1 - np.abs(t))
print("rect * rect = kolmio:",
      bool(np.max(np.abs(kolmio - tarkka)) < dt))
for ti in [-1.0, -0.5, 0.0, 0.25, 0.5]:
    i = int(np.argmin(np.abs(t - ti)))
    print(f"  t = {ti:+.2f}: {round(kolmio[i], 3) + 0.0:.3f}")
# @loppu kolmio

# @alku spektri
for fi in [0.0, 0.5, 1.0, 1.5]:
    X = np.sum(kolmio * np.exp(-2j * np.pi * fi * t)) * dt
    print(f"f = {fi:.1f}: F(kolmio) = {round(X.real, 4) + 0.0:.4f},"
          f" sinc^2 = {round(np.sinc(fi) ** 2, 4) + 0.0:.4f}")
# @loppu spektri

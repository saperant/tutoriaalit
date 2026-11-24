"""Taajuusresoluutio ja vuotaminen: kokonaiset ja vajaat jaksot."""

import numpy as np

# @alku vuotaminen
fs = 1_000.0
N = 100                                       # resoluutio fs/N = 10 Hz
t = np.arange(N) / fs
print(f"taajuusväli fs/N = {fs / N:.0f} Hz")
for f0 in (100.0, 102.5, 104.9):
    X = np.abs(np.fft.rfft(np.cos(2 * np.pi * f0 * t))) / (N / 2)
    huippu = int(np.argmax(X))
    osuus = float(np.sum(X[huippu - 1:huippu + 2] ** 2) / np.sum(X**2))
    print(f"{f0:5.1f} Hz: huippu {huippu * fs / N:3.0f} Hz,"
          f" amplitudi {X[huippu]:.3f},"
          f" kolmessa välissä {100 * osuus:5.1f} %")
# @loppu vuotaminen

# @alku vierekkaiset
# Kaksi sävelaskelen päässä olevaa taajuutta: 440 Hz ja 466 Hz.
for N in (25, 50, 100):
    t = np.arange(N) / fs
    x = np.cos(2 * np.pi * 440 * t) + np.cos(2 * np.pi * 466 * t)
    X = np.abs(np.fft.rfft(x, n=4_096))       # tiheä taajuushila
    f = np.fft.rfftfreq(4_096, d=1 / fs)
    vali = (f > 400) & (f < 500)
    # Huippujen määrä: paikalliset maksimit, jotka ylittävät puolet
    # suurimmasta.
    Xv = X[vali]
    maksimit = np.flatnonzero((Xv[1:-1] > Xv[:-2]) & (Xv[1:-1] > Xv[2:])
                              & (Xv[1:-1] > 0.5 * Xv.max()))
    print(f"N = {N:3d} (fs/N = {fs / N:4.0f} Hz): huippuja {len(maksimit)}")
# @loppu vierekkaiset

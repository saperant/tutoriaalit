"""Taajuusvaste scipy.signal.freqz:lla ja mittaus sinisyötteellä."""

import numpy as np
from scipy import signal

# @alku freqz
fs = 1_000.0
b, a = signal.butter(2, 100.0, fs=fs)         # 2. asteen alipäästö 100 Hz
taajuudet = np.array([10.0, 50.0, 100.0, 200.0, 400.0])
f, H = signal.freqz(b, a, worN=taajuudet, fs=fs)
print("   f/Hz    |H|     dB   vaihe/aste")
for fi, Hi in zip(f, H, strict=True):
    db = round(20 * np.log10(abs(Hi)), 2) + 0.0
    print(f"{fi:7.0f} {abs(Hi):6.4f} {db:6.2f}"
          f" {np.degrees(np.angle(Hi)):8.2f}")
# @loppu freqz

# @alku mittaus
# Sini sisään -> sama taajuus ulos, kerrottuna |H|:lla ja siirrettynä
# kulmalla arg H. Mitataan kompleksinen amplitudi korrelaatiolla.
n = np.arange(4_000)
for fi in f:
    x = np.cos(2 * np.pi * fi / fs * n)
    y = signal.lfilter(b, a, x)[2_000:]       # transientti ohi
    kanta = np.exp(-2j * np.pi * fi / fs * n[2_000:])
    osoitin = complex(2 * np.mean(y * kanta))
    print(f"{fi:5.0f} Hz: mitattu {abs(osoitin):6.4f}"
          f" {np.degrees(np.angle(osoitin)):8.2f} astetta")
# @loppu mittaus

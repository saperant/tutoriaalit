"""Rationaalinen naytetaajuuden muunnos 44,1 kHz -> 48 kHz."""

import math

import numpy as np
from scipy import signal

# @alku suhde
f_sisaan, f_ulos = 44_100, 48_000
g = math.gcd(f_sisaan, f_ulos)
L, M = f_ulos // g, f_sisaan // g
print(f"L = {L}, M = {M}, valitaajuus {f_sisaan * L / 1e6:.3f} MHz")
# @loppu suhde


def taso_db(y: np.ndarray, f: float, fs: float) -> float:
    k = np.exp(-2j * np.pi * f / fs * np.arange(y.size))
    db = 20 * np.log10(2 * abs(np.mean(y * k)) + 1e-12)
    return round(float(db), 1) + 0.0


# @alku muunna
n = np.arange(f_sisaan)                      # 1 s
x = np.sin(2 * np.pi * 1_000 / f_sisaan * n)
x += 0.1 * np.sin(2 * np.pi * 19_000 / f_sisaan * n)
# Oma suodin: paastokaista 20 kHz:iin, esto 22,05 kHz:sta, 90 dB.
fs_vali = f_sisaan * L
lkm, beta = signal.kaiserord(90.0, 2_050.0 / (fs_vali / 2))
h = signal.firwin(lkm, 21_025.0, window=("kaiser", beta), fs=fs_vali)
# resample_poly skaalaa kertoimet itse vahvistukseen L.
for nimi, ikkuna in (("oletus", ("kaiser", 5.0)), ("oma", h)):
    y = signal.resample_poly(x, L, M, window=ikkuna)
    keski = y[f_ulos // 4:f_ulos // 4 + f_ulos // 2]    # 0,5 s keskelta
    tasot = [taso_db(keski, f, f_ulos) for f in (1e3, 19e3, 22.9e3)]
    peili = f"{tasot[2]:.1f} dB" if tasot[2] > -100 else "alle -100 dB"
    print(f"{nimi:6s}: 1 kHz {tasot[0]:5.1f} dB, 19 kHz {tasot[1]:5.1f} dB,"
          f" peili 22,9 kHz {peili}")
print(f"oma suodin: {lkm} kerrointa, {math.ceil(lkm / L)} kertolaskua"
      " ulostulonaytetta kohti")
# @loppu muunna

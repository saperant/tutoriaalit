"""Ideaalisen alipaaston katkaisu: Gibbsin ilmio ei katoa pidentamalla."""

import numpy as np
from scipy import signal

# @alku ideaalinen
fc = 0.25                                  # rajataajuus / fs


def ideaalinen(lkm: int) -> np.ndarray:
    """Ideaalisen alipaaston impulssivaste katkaistuna (suorakaide)."""
    n = np.arange(lkm) - (lkm - 1) / 2     # symmetrinen keskikohdan ympari
    h: np.ndarray = 2 * fc * np.sinc(2 * fc * n)
    return h
# @loppu ideaalinen


# @alku mittaus
print("  N  ylitys  vaimennus  siirtyma/fs")
for lkm in (21, 81, 321):
    f, H = signal.freqz(ideaalinen(lkm), worN=1 << 16, fs=1.0)
    A = np.abs(H)
    ylitys = A[f < fc].max() - 1
    vaimennus = -20 * np.log10(A[f > fc + 1.0 / lkm].max())
    # Siirtymakaista: vahvistus putoaa arvosta 0.9 arvoon 0.1.
    leveys = f[np.argmax(A < 0.1)] - f[np.argmax(A < 0.9)]
    print(f"{lkm:3d}  {ylitys:6.4f}  {vaimennus:6.1f} dB  {leveys:9.4f}")
# @loppu mittaus

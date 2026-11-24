"""Overlap-save: pitka FIR lohkoittain FFT:lla, tila lohkojen valilla."""

import math

import numpy as np
from scipy import signal


# @alku overlap_save
class OverlapSave:
    """FIR-suodatus FFT:lla. Lohkon pituus L = N - M + 1."""

    def __init__(self, h: np.ndarray, n_fft: int) -> None:
        self.M = h.size
        if n_fft < 2 * self.M or n_fft & (n_fft - 1):
            raise ValueError("n_fft: kahden potenssi ja >= 2 * len(h)")
        self.N = n_fft
        self.L = n_fft - self.M + 1
        self.H = np.fft.rfft(h, n_fft)
        self.edellinen = np.zeros(self.M - 1)   # tila: M - 1 naytetta

    def kasittele(self, x: np.ndarray) -> np.ndarray:
        """Ottaa tasan L naytetta ja palauttaa L naytetta."""
        if x.size != self.L:
            raise ValueError(f"lohkon pituus on {self.L}")
        kehys = np.concatenate([self.edellinen, x])
        self.edellinen = kehys[-(self.M - 1):]
        y = np.fft.irfft(np.fft.rfft(kehys) * self.H, self.N)
        return y[self.M - 1:]                 # syklisesti vaaristyneet pois
# @loppu overlap_save


# @alku vertaa
rng = np.random.default_rng(5)
h = signal.firwin(255, 0.1)
os_ = OverlapSave(h, 1024)
x = rng.standard_normal(os_.L * 20)
y = np.concatenate([os_.kasittele(x[i:i + os_.L])
                    for i in range(0, x.size, os_.L)])
ero = np.max(np.abs(y - signal.lfilter(h, [1.0], x)))
print(f"lohko {os_.L}, FFT {os_.N}: ero lfilteriin alle 1e-12: {ero < 1e-12}")
# @loppu vertaa

# @alku kustannus
# Reaalikertolaskuja ulostulonaytetta kohti (karkea malli): kaksi
# reaalista FFT:ta, kumpikin noin 2 N log2 N, ja N/2 kompleksituloa.
print("   N_fft   L   kertolaskuja/nayte (suora: 255)")
for n_fft in (512, 1024, 2048, 4096, 16384):
    L = n_fft - h.size + 1
    kerto = 2 * 2 * n_fft * math.log2(n_fft) + 4 * (n_fft // 2)
    print(f"{n_fft:8d} {L:5d}   {kerto / L:6.1f}")
# @loppu kustannus

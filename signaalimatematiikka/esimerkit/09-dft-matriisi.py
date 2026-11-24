"""DFT-matriisi ja oma O(N^2)-toteutus."""

import numpy as np
from numpy.typing import NDArray

Kompleksi = NDArray[np.complex128]
Taulukko = NDArray[np.float64]


# @alku matriisi
def dft_matriisi(N: int) -> Kompleksi:
    """F[k, n] = e^(-i 2 pi k n / N)."""
    k = np.arange(N)[:, np.newaxis]
    n = np.arange(N)[np.newaxis, :]
    return np.asarray(np.exp(-2j * np.pi * k * n / N), dtype=np.complex128)


nimet = {1: "1", -1: "-1", 1j: "i", -1j: "-i"}
F = dft_matriisi(4)
print("F (N = 4):")
for rivi in F:
    print("  ".join(f"{nimet[complex(round(z.real), round(z.imag))]:>3}"
                    for z in rivi))
N = 16
F = dft_matriisi(N)
print("F^H F = N I:", bool(np.allclose(F.conj().T @ F, N * np.eye(N))))
print("F on symmetrinen:", bool(np.allclose(F, F.T)))
U = F / np.sqrt(N)
print("U = F / sqrt(N) on unitaarinen:",
      bool(np.allclose(U.conj().T @ U, np.eye(N))))
# @loppu matriisi


# @alku oma
def dft(x: Kompleksi | Taulukko) -> Kompleksi:
    """X[k] = sum_n x[n] e^(-i 2 pi k n / N), O(N^2) laskua."""
    N = len(x)
    X = np.zeros(N, dtype=np.complex128)
    for k in range(N):
        for n in range(N):
            X[k] += x[n] * np.exp(-2j * np.pi * k * n / N)
    return X


rng = np.random.default_rng(7)
x = rng.uniform(-1, 1, 64) + 1j * rng.uniform(-1, 1, 64)
print("oma silmukka = np.fft.fft:", bool(np.allclose(dft(x), np.fft.fft(x))))
print("matriisi     = np.fft.fft:",
      bool(np.allclose(dft_matriisi(64) @ x, np.fft.fft(x))))
# @loppu oma

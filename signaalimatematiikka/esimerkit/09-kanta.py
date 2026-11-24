"""DFT kannanvaihtona ja Parsevalin kaava."""

import numpy as np
from numpy.typing import NDArray

Kompleksi = NDArray[np.complex128]


def kl(z: complex, d: int = 4) -> str:
    a = round(z.real, d) + 0.0
    b = round(z.imag, d) + 0.0
    merkki = "-" if b < 0 else "+"
    return f"{a:.{d}f} {merkki} {abs(b):.{d}f}i"


def dft_matriisi(N: int) -> Kompleksi:
    """F[k, n] = e^(-i 2 pi k n / N)."""
    k = np.arange(N)[:, np.newaxis]
    n = np.arange(N)[np.newaxis, :]
    return np.asarray(np.exp(-2j * np.pi * k * n / N), dtype=np.complex128)


# @alku kanta
x8 = np.array([3.0, 1.0, -2.0, 0.5, 0.0, 1.0, 2.0, -1.0])
N = len(x8)
X8 = np.fft.fft(x8)
kantavektorit = np.conj(dft_matriisi(N))        # rivi k = e_k
for k in [0, 1, 2]:
    projektio = np.vdot(kantavektorit[k], x8)  # sum x[n] conj(e_k[n])
    print(f"X[{k}] = <x, e_{k}> = {kl(complex(projektio))}")
takaisin = kantavektorit.T @ X8 / N              # x = (1/N) sum X[k] e_k
print("x = (1/N) sum X[k] e_k:", bool(np.allclose(takaisin, x8)))
print("ifft palauttaa:", np.round(np.fft.ifft(X8).real, 6) + 0.0)
print(f"Parseval: sum |x|^2 = {np.sum(np.abs(x8) ** 2):.4f},"
      f" (1/N) sum |X|^2 = {np.sum(np.abs(X8) ** 2) / N:.4f}")
# @loppu kanta

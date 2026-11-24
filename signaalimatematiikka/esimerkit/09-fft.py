"""FFT:n idea: DFT puolitetaan parillisiin ja parittomiin näytteisiin."""

import math

import numpy as np
from numpy.typing import NDArray

Kompleksi = NDArray[np.complex128]


# @alku fft
def fft(x: Kompleksi) -> Kompleksi:
    """Rekursiivinen radix-2-FFT; len(x) on kahden potenssi."""
    N = len(x)
    if N == 1:
        return x.copy()
    parilliset = fft(x[0::2])
    parittomat = fft(x[1::2])
    w = np.exp(-2j * np.pi * np.arange(N // 2) / N)   # kiertokertoimet
    return np.concatenate([parilliset + w * parittomat,
                           parilliset - w * parittomat])


rng = np.random.default_rng(11)
for N in [8, 64, 1024]:
    x = (rng.standard_normal(N) + 1j * rng.standard_normal(N)).astype(
        np.complex128)
    print(f"N = {N:4d}: oma fft = np.fft.fft:",
          bool(np.allclose(fft(x), np.fft.fft(x))))
# @loppu fft


# @alku laskut
def kertolaskut(N: int) -> int:
    """Kompleksikertolaskut: T(N) = 2 T(N/2) + N/2, T(1) = 0."""
    return 0 if N == 1 else 2 * kertolaskut(N // 2) + N // 2


print("       N             N^2  (N/2) log2 N    suhde")
for p in [3, 6, 10, 16, 20]:
    N = 2**p
    fft_n = kertolaskut(N)
    assert fft_n == N // 2 * int(math.log2(N))
    print(f"{N:8d} {N * N:15d} {fft_n:13d} {N * N / fft_n:8.0f}")
# @loppu laskut

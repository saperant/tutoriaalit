"""Konvoluutiolause: syklinen konvoluutio ja nollilla täyttö."""

import numpy as np
from numpy.typing import NDArray

Taulukko = NDArray[np.float64]


# @alku syklinen
def syklinen(x: Taulukko, h: Taulukko) -> Taulukko:
    """y[n] = sum_k x[k] h[(n - k) mod N]."""
    N = len(x)
    return np.array([sum(x[k] * h[(n - k) % N] for k in range(N))
                     for n in range(N)])


x = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
h = np.array([1.0, -1.0, 0.5, 0.0, 0.0, 0.0])
suora = syklinen(x, h)
fft_tapa = np.real(np.fft.ifft(np.fft.fft(x) * np.fft.fft(h)))
print("syklinen määritelmästä:", suora)
print("ifft(fft(x) fft(h))   :", np.round(fft_tapa, 12) + 0.0)
# @loppu syklinen

# @alku nollat
a = np.array([1.0, 2.0, 3.0, 4.0])
b = np.array([1.0, -1.0, 0.5])
lineaarinen = np.convolve(a, b)
ilman = np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b, n=len(a))))
L = len(a) + len(b) - 1
täytetty = np.real(np.fft.ifft(np.fft.fft(a, n=L) * np.fft.fft(b, n=L)))
print("np.convolve       :", lineaarinen)
print("FFT, pituus 4     :", np.round(ilman, 12) + 0.0, "<- kiertyy")
print(f"FFT, pituus {L}     :", np.round(täytetty, 12) + 0.0)
# @loppu nollat

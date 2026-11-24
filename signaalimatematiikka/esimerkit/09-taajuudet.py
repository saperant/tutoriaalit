"""DFT:n taajuusindeksit ja reaalisen signaalin symmetria."""

import numpy as np


def kl(z: complex, d: int = 4) -> str:
    a = round(z.real, d) + 0.0
    b = round(z.imag, d) + 0.0
    merkki = "-" if b < 0 else "+"
    return f"{a:.{d}f} {merkki} {abs(b):.{d}f}i"


# @alku taajuudet
fs, N = 1000.0, 10
n = np.arange(N)
x = np.cos(2 * np.pi * 100 * n / fs) + 0.5 * np.sin(2 * np.pi * 300 * n / fs)
X = np.fft.fft(x)
f = np.fft.fftfreq(N, d=1 / fs)
print("taajuudet:", f.astype(int))
for i in np.flatnonzero(np.abs(X) > 1e-9):
    print(f"  k = {i:d}, f = {f[i]:+5.0f} Hz, X[k]/N = {kl(X[i] / N)}")
print("reaalinen signaali: X[N-k] = conj X[k]:",
      bool(np.allclose(X[1:][::-1], np.conj(X[1:]))))
# @loppu taajuudet

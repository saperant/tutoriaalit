"""DFT:n yhteys Fourier-sarjaan ja Fourier-muunnokseen."""

import numpy as np


def kl(z: complex, d: int = 4) -> str:
    a = round(z.real, d) + 0.0
    b = round(z.imag, d) + 0.0
    merkki = "-" if b < 0 else "+"
    return f"{a:.{d}f} {merkki} {abs(b):.{d}f}i"


# @alku sarja
# Trigonometrinen polynomi: DFT / N antaa Fourier-kertoimet tarkasti.
c = {0: 0.5, 1: 1 - 1j, -1: 1 + 1j, 3: 0.25j, -3: -0.25j}
N = 16
t = 2 * np.pi * np.arange(N) / N
x = np.zeros(N, dtype=np.complex128)
for k, ck in c.items():
    x += ck * np.exp(1j * k * t)
C = np.fft.fft(x) / N
for k in [0, 1, 3, -1, -3]:
    print(f"c_{k:<2d}: DFT[{k % N:2d}]/N = {kl(complex(C[k % N]))},"
          f" tarkka {kl(c[k])}")
# @loppu sarja

# @alku muunnos
# Jatkuva muunnos X(f) = int x(t) e^(-2 pi i f t) dt FFT:llä.
dt, N = 0.05, 512
aika = (np.arange(N) - N // 2) * dt            # [-12.8, 12.75]
pulssi = np.exp(-np.pi * aika**2)
# ifftshift siirtää kohdan t = 0 indeksiin 0, fftshift järjestää f:t.
X = np.fft.fftshift(np.fft.fft(np.fft.ifftshift(pulssi))) * dt
f = np.fft.fftshift(np.fft.fftfreq(N, d=dt))
print(f"taajuusväli 1/(N dt) = {f[1] - f[0]:.4f} Hz,"
      f" suurin taajuus {-f[0]:.1f} Hz")
print("FFT * dt = e^(-pi f^2):",
      bool(np.max(np.abs(X - np.exp(-np.pi * f**2))) < 1e-12))
# @loppu muunnos

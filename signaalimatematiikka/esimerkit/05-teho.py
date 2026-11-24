"""Keskiarvo, teho, tehollisarvo ja Parsevalin idea."""

import math

import numpy as np

# @alku teho
fs, T = 48000, 0.1                      # 0.1 s = 5 jaksoa 50 Hz:llä
t = np.arange(int(fs * T)) / fs
A = 325.0                               # verkkojännitteen huippuarvo
u = 12.0 + A * np.sin(2 * np.pi * 50 * t)

print(f"keskiarvo    {np.mean(u):8.3f} V")
print(f"teho <u^2>   {np.mean(u**2):8.1f} V^2")
print(f"kaava        {12.0**2 + A**2 / 2:8.1f} V^2  (DC^2 + A^2/2)")
print(f"tehollisarvo {np.sqrt(np.mean(u**2)):8.3f} V")
print(f"A/sqrt(2)    {A / math.sqrt(2):8.3f} V  (pelkkä vaihto-osa)")
# @loppu teho

# @alku parseval
# x(t) = sum c_k e^(ikt): kertoimet suoraan, teho kahdella tavalla.
c = {0: 0.5, 1: 1 - 1j, -1: 1 + 1j, 3: 0.25j, -3: -0.25j}
M = 64
tt = 2 * np.pi * np.arange(M) / M
x = sum(ck * np.exp(1j * k * tt) for k, ck in c.items())
x = np.asarray(x, dtype=np.complex128)
print("signaali on reaalinen:", bool(np.max(np.abs(x.imag)) < 1e-12))
aika = float(np.mean(np.abs(x) ** 2))
taajuus = sum(abs(ck) ** 2 for ck in c.values())
print(f"teho aikatasossa   {aika:.6f}")
print(f"teho kertoimista   {taajuus:.6f}")
for k in sorted(c):
    print(f"  k = {k:+d}: |c_k|^2 = {abs(c[k]) ** 2:.4f}"
          f" ({100 * abs(c[k]) ** 2 / taajuus:5.1f} %)")
# @loppu parseval


# @alku desibelit
def db(teho: float, viite: float = 1.0) -> float:
    return 10 * math.log10(teho / viite)


signaali = A**2 / 2
kohina = 0.5**2                         # kohinan teho (V^2)
print(f"SNR = {db(signaali, kohina):.2f} dB")
print(f"amplitudi puolittuu: {db(0.5**2):.2f} dB,"
      f" teho puolittuu: {db(0.5):.2f} dB")
print(f"kymmenkertainen amplitudi: {20 * math.log10(10):.1f} dB")
# @loppu desibelit

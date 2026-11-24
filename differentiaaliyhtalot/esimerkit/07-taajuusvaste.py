"""Taajuusvaste H(j w) ja yhteys diskreettiin aikaan (s-taso ja z-taso)."""

import cmath
import math

import numpy as np
from scipy import signal

# @alku taajuus
# Sama RLC-alipäästö kuin edellä:
# H(s) = w0^2 / (s^2 + 2 zeta w0 s + w0^2),
# w0 = 10 000 rad/s, zeta = 0,1. Sinitulon amplitudi kerrotaan |H(j w)|:lla.
w0, zeta = 1e4, 0.1
osoittaja, nimittaja = [w0**2], [1.0, 2 * zeta * w0, w0**2]
for w in (1e3, 1e4, 1e5):
    Hj = w0**2 / ((1j * w) ** 2 + 2 * zeta * w0 * (1j * w) + w0**2)
    print(
        f"w = {w:8.0f}: |H| = {abs(Hj):7.4f} "
        f"({20 * math.log10(abs(Hj)):6.1f} dB), "
        f"vaihe {math.degrees(cmath.phase(Hj)):7.1f} astetta"
    )
_, vaste = signal.freqs(osoittaja, nimittaja, worN=[1e4])
print(f"scipy.signal.freqs, w = 10000: |H| = {abs(vaste[0]):.4f}")
# @loppu taajuus

# @alku diskreetti
# Näytteistetty järjestelmä: jatkuvan ajan napa s vastaa z-tason napaa
# z = exp(s T). Vakaa alue Re s < 0 kuvautuu yksikköympyrän sisään.
T = 1e-5  # näytteenottoväli 100 kHz
# Tilaesityksen kautta: tf2ss ja cont2discrete, navat A_d:n ominaisarvoina.
A, B, C, D = signal.tf2ss(osoittaja, nimittaja)
Ad = signal.cont2discrete((A, B, C, D), T, method="zoh")[0]
z_navat = np.linalg.eigvals(Ad)
s_navat = np.roots(nimittaja)
for sn in sorted(s_navat, key=lambda z: z.imag):
    odotettu = np.exp(sn * T)
    lahin = min(z_navat, key=lambda z: abs(z - odotettu))
    print(
        f"s = {sn.real:.0f}{sn.imag:+.1f}j -> z = {lahin.real:.6f}"
        f"{lahin.imag:+.6f}j, |z| = {abs(lahin):.6f}"
    )
# @loppu diskreetti

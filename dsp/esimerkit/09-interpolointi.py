"""Interpolointi: nollien lisays tuottaa peilikuvat, suodin poistaa ne."""

import numpy as np
from scipy import signal

fs, L = 12_000.0, 4                         # 12 kHz -> 48 kHz
n = np.arange(12_000)
x = np.sin(2 * np.pi * 1_000.0 / fs * n)


def taso_db(y: np.ndarray, f: float, fs_y: float) -> float:
    k = np.exp(-2j * np.pi * f / fs_y * np.arange(y.size))
    db = 20 * np.log10(2 * abs(np.mean(y * k)) + 1e-12)
    return round(float(db), 1) + 0.0


# @alku nollat
tihennetty = np.zeros(x.size * L)
tihennetty[::L] = x                         # L - 1 nollaa naytteiden valiin
h = L * signal.firwin(97, 5_000.0, window=("kaiser", 8.0), fs=fs * L)
y = signal.lfilter(h, [1.0], tihennetty)
for nimi, z in (("nollat lisatty", tihennetty), ("suodatettu", y)):
    z = z[-24_000:]                         # 0,5 s
    tasot = [taso_db(z, f, fs * L) for f in (1_000.0, 11_000.0, 13_000.0)]
    print(f"{nimi:15s} 1 kHz {tasot[0]:6.1f} dB, peilit"
          f" {tasot[1]:6.1f} dB (11 kHz), {tasot[2]:6.1f} dB (13 kHz)")
# @loppu nollat

# @alku valmis
# Sama valmiina: upfirdn tekee nollien lisayksen ja suodatuksen
# laskematta nollilla kerrottuja termeja.
valmis = signal.upfirdn(h, x, up=L)[:y.size]
print(f"upfirdn == lfilter(nollat): {np.allclose(valmis, y, atol=1e-12)}")
# @loppu valmis

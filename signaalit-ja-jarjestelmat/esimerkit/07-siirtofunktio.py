"""Siirtofunktio H(z) = B(z)/A(z): navat, nollat ja ominaisjonot z^n."""

import numpy as np
from scipy import signal

# @alku siirtofunktio
# y[n] = x[n] + x[n-1] + 0.9 y[n-1] - 0.5 y[n-2]
b = np.array([1.0, 1.0])
a = np.array([1.0, -0.9, 0.5])
nollat, navat, k = signal.tf2zpk(b, a)
print("nollat:", ", ".join(f"{complex(z):.4f}" for z in nollat))
print("navat: ", ", ".join(f"{complex(p):.4f}" for p in navat))
print("|navat|:", ", ".join(f"{abs(p):.4f}" for p in navat), f" k = {k:g}")
# @loppu siirtofunktio


# @alku ominaisjono
def H(z: complex) -> complex:
    """B(z)/A(z) potensseina z^-1."""
    zi = 1 / z
    return complex(np.polyval(b[::-1], zi) / np.polyval(a[::-1], zi))


# Syöte z0^n tuottaa (alkutransientin jälkeen) ulostulon H(z0) z0^n.
for z0 in (1.0 + 0.0j, 0.95 * np.exp(0.5j), 1.2 + 0.0j):
    n = np.arange(300)
    x = z0**n
    y = signal.lfilter(b, a, x)
    suhde = complex(y[-1] / x[-1])
    print(f"z0 = {complex(z0):.3f}: y/x = {suhde:.4f},"
          f" H(z0) = {H(z0):.4f}")
# @loppu ominaisjono

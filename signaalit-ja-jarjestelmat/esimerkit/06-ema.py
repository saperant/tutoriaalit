"""Eksponentiaalinen liukuva keskiarvo: aikavakio ja kohinan vaimennus."""

import math

import numpy as np
from scipy import signal

# @alku ema
fs = 1_000.0                             # Hz
tau = 0.020                              # haluttu aikavakio 20 ms
alfa = 1 - math.exp(-1 / (fs * tau))     # y[n] = y[n-1] + alfa (x - y)
b, a = [alfa], [1.0, -(1 - alfa)]
print(f"alfa = {alfa:.5f}")

askel = np.ones(200)
y = signal.lfilter(b, a, askel)
n63 = int(np.argmax(y >= 1 - math.exp(-1)))
n95 = int(np.argmax(y >= 0.95))
print(f"63 % saavutetaan {n63} ms:ssa, 95 % {n95} ms:ssa"
      f" (3 tau = {3e3 * tau:.0f} ms)")
# @loppu ema

# @alku kohina
rng = np.random.default_rng(4)
kohina = rng.normal(size=200_000)
suodatettu = signal.lfilter(b, a, kohina)[1_000:]
teoria = math.sqrt(alfa / (2 - alfa))    # sum h^2 = alfa^2/(1-(1-alfa)^2)
print(f"kohinan keskihajonta {np.std(suodatettu):.4f},"
      f" teoria {teoria:.4f}")
print(f"vastaava liukuva keskiarvo: M = {(2 - alfa) / alfa:.1f} näytettä")
# @loppu kohina

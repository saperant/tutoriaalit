"""Askelvaste kapasitiivisella kuormalla: malli ja SPICE."""

import math

import numpy as np
from scipy import signal

from spice import lopeta, simuloi, vertaa

# @alku malli
A_ol, GBW, f_p2, R_ulos, C_L = 1e5, 10e6, 30e6, 50.0, 1e-9
p1 = 2 * math.pi * GBW / A_ol
p2 = 2 * math.pi * f_p2
pL = 1 / (R_ulos * C_L)
# Silmukkavahvistus T(s) = A_ol / ((1 + s/p1)(1 + s/p2)(1 + s/pL)) ja
# seuraajan suljettu silmukka H = T / (1 + T).
nimittaja = np.polymul(np.polymul([1 / p1, 1], [1 / p2, 1]), [1 / pL, 1])
H = ([A_ol], list(np.polyadd(nimittaja, [A_ol])))
t, y = signal.step(H, T=np.linspace(0, 6e-6, 30001))
ylitys_malli = float(y.max() / y[-1] - 1)
# @loppu malli

tulos = simuloi("05-askel.cir").arvot
askel = 0.01
vertaa("ylitys", tulos["suora"] / askel - 1, ylitys_malli, "", 0.05)
print(f"eristysvastuksen kanssa ylitys "
      f"{100 * (tulos['eristetty'] / askel - 1):.0f} %")
lopeta()

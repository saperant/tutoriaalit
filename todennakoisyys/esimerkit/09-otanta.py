"""Otanta jakaumista: käänteisfunktiomenetelmä ja hylkäysmenetelmä."""

import math

import numpy as np

rng = np.random.default_rng(41)
n = 500_000

# @alku kaanteis
# Exp(lam): F(x) = 1 - exp(-lam x), joten X = -ln(1 - U) / lam.
lam = 2.0
u = rng.random(n)
x = -np.log1p(-u) / lam
print(f"käänteisfunktio Exp(2): keskiarvo {float(x.mean()):.4f}"
      f" (teoria 0.5000), mediaani {float(np.median(x)):.4f}"
      f" (teoria {math.log(2) / lam:.4f})")
# @loppu kaanteis


# @alku hylkays
def tiheys(t: float) -> float:
    """Puoliympyrän tiheys välillä [-1, 1]: (2/pi) sqrt(1 - t^2)."""
    return 2 / math.pi * math.sqrt(1 - t * t)


# Ehdotus tasajakaumasta, kirjekuori M * g(t), jossa g = 1/2 ja M = 4/pi.
M = 4 / math.pi
hyvaksytyt: list[float] = []
ehdotuksia = 0
while len(hyvaksytyt) < 100_000:
    t = float(rng.uniform(-1.0, 1.0))
    ehdotuksia += 1
    if rng.random() * M * 0.5 <= tiheys(t):
        hyvaksytyt.append(t)
h = np.array(hyvaksytyt)
print(f"hylkäys: hyväksymisosuus {len(h) / ehdotuksia:.3f}"
      f" (teoria 1/M = {1 / M:.3f}), varianssi {float(h.var()):.4f}"
      f" (teoria 0.2500)")
# @loppu hylkays

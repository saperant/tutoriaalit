"""Jäykkä yhtälö: eksplisiittinen menetelmä vaatii pienet askeleet."""

import numpy as np
from scipy.integrate import solve_ivp

# @alku jaykka
# y' = -1000 (y - cos t), y(0) = 0. Ratkaisu seuraa hitaasti muuttuvaa
# funktiota cos t, mutta nopea aikavakio 1/1000 rajoittaa eksplisiittisen
# menetelmän askelta vakauden vuoksi, ei tarkkuuden.
LAMBDA = 1000.0


def f(t: float, y: np.ndarray) -> np.ndarray:
    tulos: np.ndarray = -LAMBDA * (y - np.cos(t))
    return tulos


for menetelma in ("RK45", "Radau", "BDF"):
    r = solve_ivp(f, (0, 10), [0.0], method=menetelma, rtol=1e-6, atol=1e-9)
    print(
        f"{menetelma:6s} askelia {len(r.t) - 1:5d}, y(10) = {r.y[0, -1]:.6f}"
    )
# @loppu jaykka

# @alku euler
# Eksplisiittinen Euler on vakaa vain, kun |1 - h LAMBDA| <= 1, eli
# h <= 2/LAMBDA = 0,002. Implisiittinen Euler on vakaa kaikilla h.
for h in (0.0019, 0.0021):
    y = 0.0
    yi = 0.0
    t = 0.0
    for _ in range(int(round(1 / h))):
        y = y + h * float(f(t, np.array([y]))[0])
        # Implisiittinen: y_uusi = y + h f(t + h, y_uusi) ratkaistuna.
        yi = (yi + h * LAMBDA * np.cos(t + h)) / (1 + h * LAMBDA)
        t += h
    print(f"h = {h}: eksplisiittinen y(1) = {y:.4g}, implisiittinen {yi:.6f}")
# @loppu euler

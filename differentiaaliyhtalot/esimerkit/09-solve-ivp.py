"""SciPyn solve_ivp: toleranssit, tiheä tuloste ja tapahtumat."""

import math

import numpy as np
from scipy.integrate import solve_ivp


# @alku putoaminen
# Pallo putoaa 100 m korkeudelta ilmanvastuksen kanssa:
# v' = g - (k/m) v^2, h' = -v. Milloin pallo osuu maahan?
G, K_PER_M = 9.81, 0.02


def f(_t: float, z: np.ndarray) -> np.ndarray:
    h, v = z
    return np.array([-v, G - K_PER_M * v * v])


def maassa(_t: float, z: np.ndarray) -> float:
    return float(z[0])


maassa.terminal = True  # type: ignore[attr-defined]

for rtol in (1e-3, 1e-6, 1e-9):
    r = solve_ivp(
        f, (0, 60), [100.0, 0.0], events=maassa, rtol=rtol, atol=rtol * 1e-3
    )
    print(
        f"rtol {rtol:.0e}: osuma {r.t_events[0][0]:.6f} s, "
        f"nopeus {r.y_events[0][0][1]:.4f} m/s, {r.nfev} kutsua"
    )
print(f"rajanopeus sqrt(g m/k) = {math.sqrt(G / K_PER_M):.4f} m/s")
# @loppu putoaminen

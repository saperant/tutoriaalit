"""Kun ratkaisu ei ole yksikäsitteinen: y' = sqrt(|y|), y(0) = 0."""

import math

import numpy as np
from scipy.integrate import solve_ivp


# @alku kaksi
# Sekä y = 0 että y = t^2/4 (t >= 0) toteuttavat yhtälön ja alkuehdon.
def f(_t: float, y: np.ndarray) -> np.ndarray:
    return np.sqrt(np.abs(y))


for nimi, ratkaisu in (
    ("y = 0", lambda s: 0.0),
    ("y = t^2/4", lambda s: s * s / 4),
):
    s = 2.0
    h = 1e-6
    derivaatta = (ratkaisu(s + h) - ratkaisu(s - h)) / (2 * h)
    print(
        f"{nimi:10s} y'(2) = {derivaatta:.6f}, "
        f"sqrt|y(2)| = {math.sqrt(abs(ratkaisu(s))):.6f}"
    )

# Numeerinen ratkaisija valitsee tasan nollasta alkaessaan ratkaisun y = 0.
nolla = solve_ivp(f, (0, 2), [0.0])
pieni = solve_ivp(f, (0, 2), [1e-12], rtol=1e-8, atol=1e-12)
print(f"y(0) = 0:      y(2) = {nolla.y[0, -1]:.4f}")
print(f"y(0) = 1e-12:  y(2) = {pieni.y[0, -1]:.4f}")
# @loppu kaksi

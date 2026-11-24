"""Hilbertin matriisi: pieni jäännös ei takaa pientä virhettä."""

import warnings

import numpy as np
from scipy import linalg

EPS = float(np.finfo(float).eps)


def kylla(ehto: bool) -> str:
    return "kyllä" if ehto else "ei"


# @alku hilbert
print(" n  cond   jäännös < 1e-14  virhe <= cond eps  virhe < 1e-6")
for n in (4, 8, 10, 12):
    H = linalg.hilbert(n)              # H[i, j] = 1 / (i + j + 1)
    oikea = np.ones(n)
    b = H @ oikea
    with warnings.catch_warnings():
        # SciPy varoittaa huonokuntoisesta matriisista; tässä se tiedetään.
        warnings.simplefilter("ignore", linalg.LinAlgWarning)
        x = linalg.solve(H, b)
    kappa = float(np.linalg.cond(H))
    jaannos = float(np.linalg.norm(H @ x - b) / np.linalg.norm(b))
    virhe = float(np.linalg.norm(x - oikea) / np.linalg.norm(oikea))
    print(f"{n:2d}  {kappa:.0e}  {kylla(jaannos < 1e-14):15s}  "
          f"{kylla(virhe <= 10 * kappa * EPS):17s}  "
          f"{kylla(virhe < 1e-6)}")
# @loppu hilbert

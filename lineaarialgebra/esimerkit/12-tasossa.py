"""Homogeeniset koordinaatit tasossa: siirto matriisina."""

import math

import numpy as np
import numpy.typing as npt

Matriisi = npt.NDArray[np.float64]


def muoto(p: Matriisi) -> str:
    return " ".join(f"({round(x, 2) + 0.0:.2f}, {round(y, 2) + 0.0:.2f})"
                    for x, y in (p[:2] / p[2]).T)


# @alku muunnokset
def siirto(dx: float, dy: float) -> Matriisi:
    return np.array([[1.0, 0.0, dx], [0.0, 1.0, dy], [0.0, 0.0, 1.0]])


def kierto(asteet: float) -> Matriisi:
    t = math.radians(asteet)
    return np.array([[math.cos(t), -math.sin(t), 0.0],
                     [math.sin(t), math.cos(t), 0.0],
                     [0.0, 0.0, 1.0]])


def skaalaus(s: float) -> Matriisi:
    return np.diag([s, s, 1.0])
# @loppu muunnokset


# @alku keskipiste
# Pelihahmon (neliö 2×2, keskipiste (5, 3)) kierto oman keskipisteensä
# ympäri: siirto origoon, kierto, siirto takaisin. Yksi matriisi.
hahmo = np.array([[4.0, 6.0, 6.0, 4.0],
                  [2.0, 2.0, 4.0, 4.0],
                  [1.0, 1.0, 1.0, 1.0]])      # pisteet, w = 1
M = siirto(5, 3) @ kierto(90) @ siirto(-5, -3)
print("origon ympäri:      ", muoto(kierto(90) @ hahmo))
print("keskipisteen ympäri:", muoto(M @ hahmo))
# @loppu keskipiste

# @alku suunta
# Suunnalla (w = 0) siirto ei vaikuta: nopeusvektori kääntyy mutta ei
# siirry, kun hahmo liikkuu.
nopeus = np.array([1.0, 0.0, 0.0])
print("nopeus siirron jälkeen:", (siirto(5, 3) @ nopeus).tolist())
print("nopeus kierron jälkeen:", (np.round(kierto(90) @ nopeus, 6)
                                  + 0.0).tolist())
# @loppu suunta

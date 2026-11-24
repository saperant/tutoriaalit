"""Matriisi kuvauksena: kierto, skaalaus, leikkaus ja yhdistäminen."""

import math

import numpy as np
import numpy.typing as npt

Matriisi = npt.NDArray[np.float64]


def muoto(pisteet: Matriisi) -> str:
    """Sarakkeina annetut pisteet muodossa (x, y)."""
    return " ".join(f"({round(x, 2) + 0.0:.2f}, {round(y, 2) + 0.0:.2f})"
                    for x, y in pisteet.T)


# @alku kuvaukset
def kierto(asteet: float) -> Matriisi:
    t = math.radians(asteet)
    return np.array([[math.cos(t), -math.sin(t)],
                     [math.sin(t), math.cos(t)]])


def skaalaus(sx: float, sy: float) -> Matriisi:
    return np.array([[sx, 0.0], [0.0, sy]])


def leikkaus(k: float) -> Matriisi:
    """Vaakaleikkaus: x' = x + k·y (kursivointi)."""
    return np.array([[1.0, k], [0.0, 1.0]])


# Yksikköneliön kärjet sarakkeina.
nelio = np.array([[0.0, 1.0, 1.0, 0.0],
                  [0.0, 0.0, 1.0, 1.0]])
print("neliö:    ", muoto(nelio))
print("kierto 90:", muoto(kierto(90) @ nelio))
print("skaalaus: ", muoto(skaalaus(2, 0.5) @ nelio))
print("leikkaus: ", muoto(leikkaus(0.5) @ nelio))
# @loppu kuvaukset

# @alku sarakkeet
# Matriisin sarakkeet kertovat, mihin kantavektorit e1 ja e2 kuvautuvat.
A = kierto(30)
print("A e1 =", muoto(A @ np.array([[1.0], [0.0]])), "= 1. sarake")
print("A e2 =", muoto(A @ np.array([[0.0], [1.0]])), "= 2. sarake")
# @loppu sarakkeet

# @alku yhdistaminen
# Ensin skaalaus, sitten kierto: tulossa oikeanpuoleisin tehdään ensin.
S, R = skaalaus(2, 1), kierto(90)
print("R·S:", muoto(R @ S @ nelio))
print("S·R:", muoto(S @ R @ nelio))
print("järjestyksellä on väliä:", not np.allclose(R @ S, S @ R))
print("kierrot vaihtuvat keskenään:",
      np.allclose(kierto(30) @ kierto(60), kierto(60) @ kierto(30)))
# @loppu yhdistaminen

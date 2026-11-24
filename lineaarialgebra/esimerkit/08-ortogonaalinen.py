"""Ortogonaalinen matriisi säilyttää pituudet ja ajautuu pyöristyksessä."""

import math
from typing import Any

import numpy as np
import numpy.typing as npt

Matriisi = npt.NDArray[np.float64]


def kierto_z(asteet: float) -> Matriisi:
    t = math.radians(asteet)
    return np.array([[math.cos(t), -math.sin(t), 0.0],
                     [math.sin(t), math.cos(t), 0.0],
                     [0.0, 0.0, 1.0]])


def kierto_x(asteet: float) -> Matriisi:
    t = math.radians(asteet)
    return np.array([[1.0, 0.0, 0.0],
                     [0.0, math.cos(t), -math.sin(t)],
                     [0.0, math.sin(t), math.cos(t)]])


# @alku sailyttaa
Q = kierto_z(35) @ kierto_x(-20)
u, v = np.array([1.0, 2.0, 2.0]), np.array([2.0, -1.0, 0.5])
print("Q^T Q = I:", bool(np.allclose(Q.T @ Q, np.eye(3))))
print("pituus säilyy:",
      bool(np.isclose(np.linalg.norm(Q @ u), np.linalg.norm(u))))
print("pistetulo säilyy:", bool(np.isclose((Q @ u) @ (Q @ v), u @ v)))
print(f"det Q = {np.linalg.det(Q):.6f}")
# @loppu sailyttaa

# @alku ajautuminen
# Peli kääntää kappaletta joka ruudussa pienen kulman verran ja
# kertoo asentomatriisin uudella kierrolla. Float32-laskennassa
# pyöristysvirhe kertyy, ja matriisi lakkaa olemasta kierto.
def virhe(m: npt.NDArray[np.floating[Any]]) -> float:
    return float(np.linalg.norm(m.T @ m - np.eye(3)))


askel = (kierto_z(0.7) @ kierto_x(0.3)).astype(np.float32)
asento = np.eye(3, dtype=np.float32)
for ruutu in range(1, 100_001):
    asento = asento @ askel
    if ruutu in (1_000, 100_000):
        print(f"{ruutu:>7} ruutua: virhe {'pieni' if virhe(asento) < 1e-4
                                          else 'kasvanut'}")
# Uudelleenortogonalisointi: QR-hajotelman Q on lähin kierto
# (etumerkit korjataan, jotta R:n lävistäjä on positiivinen).
q, r = np.linalg.qr(asento.astype(np.float64))
korjattu = q * np.sign(np.diag(r))
print("korjauksen jälkeen virhe < 1e-12:", virhe(korjattu) < 1e-12)
# @loppu ajautuminen

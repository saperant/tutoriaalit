"""Pikaoppaan NumPy-muistilista: jokainen rivi on ajettu ja tarkistettu."""

import numpy as np

A = np.array([[4.0, 1.0], [2.0, 3.0]])
b = np.array([1.0, 2.0])
u, v = np.array([1.0, 2.0, 2.0]), np.array([2.0, 0.0, 1.0])

# @alku numpy
tulokset = {
    "u @ v": u @ v,                               # pistetulo
    "np.cross(u, v)": np.cross(u, v),             # ristitulo
    "np.linalg.norm(u)": np.linalg.norm(u),       # pituus
    "A @ b": A @ b,                               # matriisi × vektori
    "A.T": A.T,                                   # transpoosi
    "np.linalg.solve(A, b)": np.linalg.solve(A, b),
    "np.linalg.det(A)": np.linalg.det(A),
    "np.linalg.matrix_rank(A)": np.linalg.matrix_rank(A),
    "np.linalg.eigvals(A)": np.sort(np.linalg.eigvals(A).real),
    "np.linalg.cond(A)": np.linalg.cond(A),
}
for lauseke, arvo in tulokset.items():
    teksti = str((np.round(np.asarray(arvo, dtype=float), 3)
                  + 0.0).tolist())
    print(f"{lauseke:<26} {teksti}")
# @loppu numpy

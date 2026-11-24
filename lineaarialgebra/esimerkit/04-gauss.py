"""Gaussin eliminointi osittaistuennalla ja takaisinsijoitus."""

import numpy as np

Vektori = list[float]
Matriisi = list[list[float]]


# @alku gauss
def ratkaise(a: Matriisi, b: Vektori) -> Vektori:
    """Ratkaisee yhtälöryhmän Ax = b. Ei muuta argumentteja."""
    n = len(a)
    m = [rivi[:] + [bi] for rivi, bi in zip(a, b, strict=True)]
    for k in range(n):
        # Osittaistuenta: tukialkioksi itseisarvoltaan suurin.
        p = max(range(k, n), key=lambda i: abs(m[i][k]))
        if abs(m[p][k]) < 1e-12:
            raise ValueError("matriisi on singulaarinen")
        m[k], m[p] = m[p], m[k]
        for i in range(k + 1, n):
            kerroin = m[i][k] / m[k][k]
            for j in range(k, n + 1):
                m[i][j] -= kerroin * m[k][j]
    # Takaisinsijoitus ylhäältä alas kolmiomuodosta.
    x = [0.0] * n
    for i in reversed(range(n)):
        s = sum(m[i][j] * x[j] for j in range(i + 1, n))
        x[i] = (m[i][n] - s) / m[i][i]
    return x
# @loppu gauss


# @alku piiri
# Kolmen silmukan virtapiiri: Kirchhoffin jännitelaki antaa yhtälön
# kustakin silmukasta. Tuntemattomat ovat silmukkavirrat (A).
R = [[15.0, -5.0, 0.0],
     [-5.0, 20.0, -10.0],
     [0.0, -10.0, 25.0]]
U = [12.0, 0.0, 5.0]
virrat = ratkaise(R, U)
print("silmukkavirrat:", ", ".join(f"{i * 1000:.1f} mA" for i in virrat))
print("NumPy sama:", np.allclose(np.linalg.solve(R, U), virrat))
# @loppu piiri

try:
    ratkaise([[1.0, 2.0], [2.0, 4.0]], [1.0, 2.0])
except ValueError as virhe:
    print("riippuvat yhtälöt:", virhe)

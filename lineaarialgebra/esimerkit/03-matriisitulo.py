"""Matriisitulo ja transpoosi omana toteutuksena ja NumPylla."""

import numpy as np

Matriisi = list[list[float]]


# @alku tulo
def tulo(a: Matriisi, b: Matriisi) -> Matriisi:
    """(m×n)(n×p) = m×p; alkio c[i][j] on a:n rivin i ja b:n sarakkeen j
    pistetulo."""
    n = len(b)
    if any(len(rivi) != n for rivi in a):
        raise ValueError("a:n sarakkeiden määrä ≠ b:n rivien määrä")
    p = len(b[0])
    return [[sum(a[i][k] * b[k][j] for k in range(n)) for j in range(p)]
            for i in range(len(a))]


def transpoosi(a: Matriisi) -> Matriisi:
    return [list(sarake) for sarake in zip(*a, strict=True)]
# @loppu tulo


# @alku tarkistus
A = [[1.0, 2.0, 0.0], [0.0, 1.0, -1.0]]          # 2×3
B = [[2.0, 1.0], [0.0, 3.0], [1.0, 1.0]]         # 3×2
C = tulo(A, B)
print("A·B =", C)
print("NumPy sama:", np.allclose(np.array(A) @ np.array(B), C))
print("(AB)^T = B^T A^T:",
      transpoosi(C) == tulo(transpoosi(B), transpoosi(A)))
print("B·A on 3×3:", len(tulo(B, A)), "×", len(tulo(B, A)[0]))
try:
    tulo(A, A)
except ValueError as virhe:
    print("A·A:", virhe)
# @loppu tarkistus

# @alku hinta
# Tulossa on m·n·p kertolaskua. Kahden 1000×1000-matriisin tulo vaatii
# miljardi kertolaskua, mikä puhtaalla Pythonilla kestää minuutteja.
for n in (10, 100, 1000):
    print(f"n={n:>4}: {n ** 3:>13,} kertolaskua".replace(",", " "))
# @loppu hinta

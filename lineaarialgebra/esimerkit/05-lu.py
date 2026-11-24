"""LU-hajotelma: yksi hajotus, monta oikeaa puolta."""

import numpy as np

Vektori = list[float]
Matriisi = list[list[float]]


# @alku lu
def lu(a: Matriisi) -> tuple[list[int], Matriisi]:
    """PA = LU osittaistuennalla. Palauttaa rivien järjestyksen ja
    yhteen matriisiin pakatut L (lävistäjän alla) ja U (lävistäjällä ja
    sen yllä). L:n lävistäjä on ykkösiä, joten sitä ei tallenneta."""
    n = len(a)
    m = [rivi[:] for rivi in a]
    jarjestys = list(range(n))
    for k in range(n):
        p = max(range(k, n), key=lambda i: abs(m[i][k]))
        if abs(m[p][k]) < 1e-12:
            raise ValueError("matriisi on singulaarinen")
        m[k], m[p] = m[p], m[k]
        jarjestys[k], jarjestys[p] = jarjestys[p], jarjestys[k]
        for i in range(k + 1, n):
            m[i][k] /= m[k][k]                  # L:n alkio talteen
            for j in range(k + 1, n):
                m[i][j] -= m[i][k] * m[k][j]
    return jarjestys, m


def lu_ratkaise(jarjestys: list[int], m: Matriisi, b: Vektori) -> Vektori:
    """Ly = Pb eteenpäin ja Ux = y taaksepäin: n² operaatiota."""
    n = len(m)
    y = [b[i] for i in jarjestys]
    for i in range(n):
        y[i] -= sum(m[i][j] * y[j] for j in range(i))
    x = [0.0] * n
    for i in reversed(range(n)):
        s = sum(m[i][j] * x[j] for j in range(i + 1, n))
        x[i] = (y[i] - s) / m[i][i]
    return x
# @loppu lu


# @alku sauva
# Lämpö sauvassa: viiden sisäpisteen lämpötilat, kun päiden
# lämpötilat vaihtelevat. Matriisi pysyy samana, oikea puoli vaihtuu.
n = 5
A = [[2.0 if i == j else -1.0 if abs(i - j) == 1 else 0.0
      for j in range(n)] for i in range(n)]
jarjestys, m = lu(A)
for vasen, oikea in [(0.0, 100.0), (20.0, 20.0), (80.0, -10.0)]:
    b = [vasen] + [0.0] * (n - 2) + [oikea]
    x = lu_ratkaise(jarjestys, m, b)
    print(f"päät {vasen:5.1f} ja {oikea:5.1f}:",
          " ".join(f"{t:5.1f}" for t in x),
          "ok" if np.allclose(np.linalg.solve(A, b), x) else "VIRHE")
# @loppu sauva

# @alku hinta
for koko in (100, 1000):
    hajotus = 2 * koko ** 3 // 3
    print(f"n={koko}: hajotus ~{hajotus:.1e} op, "
          f"yksi ratkaisu ~{2 * koko ** 2:.1e} op")
# @loppu hinta

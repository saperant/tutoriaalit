"""Determinantti: pinta-alan muutos ja suunta."""

import math

import numpy as np

Matriisi = list[list[float]]


# @alku det2
def det2(a: Matriisi) -> float:
    return a[0][0] * a[1][1] - a[0][1] * a[1][0]


kuvaukset = {
    "skaalaus 2 × 3": [[2.0, 0.0], [0.0, 3.0]],
    "kierto 40°": [[math.cos(math.radians(40)), -math.sin(math.radians(40))],
                   [math.sin(math.radians(40)), math.cos(math.radians(40))]],
    "leikkaus": [[1.0, 0.7], [0.0, 1.0]],
    "peilaus x-akselin yli": [[1.0, 0.0], [0.0, -1.0]],
    "litistys suoralle": [[1.0, 2.0], [0.5, 1.0]],
}
for nimi, a in kuvaukset.items():
    d = det2(a)
    suunta = "kääntyy" if d < 0 else "säilyy" if d > 0 else "litistyy"
    print(f"{nimi:<22} det = {round(d, 3) + 0.0:6.3f}  "
          f"ala ×{abs(d):5.3f}, suunta {suunta}")
# @loppu det2

# @alku lu
def determinantti(a: Matriisi) -> float:
    """Determinantti eliminoinnilla: lävistäjän tulo, etumerkki
    vaihtuu jokaisessa rivinvaihdossa. Työ n³ eikä n!."""
    m = [rivi[:] for rivi in a]
    n, tulos = len(m), 1.0
    for k in range(n):
        p = max(range(k, n), key=lambda i: abs(m[i][k]))
        if m[p][k] == 0:
            return 0.0
        if p != k:
            m[k], m[p] = m[p], m[k]
            tulos = -tulos
        tulos *= m[k][k]
        for i in range(k + 1, n):
            kerroin = m[i][k] / m[k][k]
            for j in range(k, n):
                m[i][j] -= kerroin * m[k][j]
    return tulos


A = [[2.0, 1.0, 0.0], [1.0, 3.0, 1.0], [0.0, 1.0, 4.0]]
print(f"3×3: {determinantti(A):.3f}, NumPy {np.linalg.det(A):.3f}")
B = [[1.0, 2.0], [3.0, 4.0]]
BB: Matriisi = (np.array(B) @ np.array(B)).tolist()
print("det(BB) = det(B)²:", math.isclose(det2(BB), det2(B) ** 2))
# @loppu lu

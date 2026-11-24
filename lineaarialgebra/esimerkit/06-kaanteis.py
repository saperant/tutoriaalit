"""Käänteismatriisi Gaussin–Jordanin menetelmällä ja kuvauksen kumoaminen."""

import numpy as np

Matriisi = list[list[float]]


# @alku gauss-jordan
def kaanteis(a: Matriisi) -> Matriisi:
    """Rivioperaatiot muuttavat [A | I]:n muotoon [I | A^-1]."""
    n = len(a)
    m = [rivi[:] + [1.0 if i == j else 0.0 for j in range(n)]
         for i, rivi in enumerate(a)]
    for k in range(n):
        p = max(range(k, n), key=lambda i: abs(m[i][k]))
        if abs(m[p][k]) < 1e-12:
            raise ValueError("matriisilla ei ole käänteismatriisia")
        m[k], m[p] = m[p], m[k]
        tuki = m[k][k]
        m[k] = [x / tuki for x in m[k]]
        for i in range(n):
            if i != k:
                kerroin = m[i][k]
                m[i] = [x - kerroin * y
                        for x, y in zip(m[i], m[k], strict=True)]
    return [rivi[n:] for rivi in m]
# @loppu gauss-jordan


# @alku kumoaminen
# Kuvaus venyttää ja kallistaa. Käänteiskuvaus palauttaa pisteet.
A = [[2.0, 1.0], [0.0, 1.0]]
A_inv = kaanteis(A)
print("A^-1 =", [[round(x, 3) + 0.0 for x in rivi] for rivi in A_inv])
piste = np.array([3.0, 2.0])
kuva = np.array(A) @ piste
print("piste", piste, "-> kuva", kuva, "-> takaisin", np.array(A_inv) @ kuva)
print("A·A^-1 = I:", np.allclose(np.array(A) @ np.array(A_inv), np.eye(2)))
print("NumPy sama:", np.allclose(np.linalg.inv(A), A_inv))
# @loppu kumoaminen

try:
    kaanteis([[1.0, 2.0], [2.0, 4.0]])
except ValueError as virhe:
    print("singulaarinen:", virhe)

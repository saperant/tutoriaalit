"""Ominaisarvot käsin: 2 × 2 -matriisin karakteristinen yhtälö."""

import cmath
import math

import numpy as np

Matriisi = list[list[float]]


# @alku karakteristinen
def ominaisarvot_2x2(a: Matriisi) -> tuple[complex, complex]:
    """det(A - λI) = λ² - (jälki)λ + det = 0 toisen asteen kaavalla."""
    jalki = a[0][0] + a[1][1]
    det = a[0][0] * a[1][1] - a[0][1] * a[1][0]
    juuri = cmath.sqrt(jalki * jalki - 4 * det)
    return (jalki + juuri) / 2, (jalki - juuri) / 2


def teksti(z: complex) -> str:
    if abs(z.imag) < 1e-12:
        return f"{z.real:.4f}"
    return f"{z.real:.4f}{z.imag:+.4f}i"


t = math.radians(60)
matriisit: dict[str, Matriisi] = {
    "symmetrinen [[2, 1], [1, 2]]": [[2.0, 1.0], [1.0, 2.0]],
    "Fibonacci [[1, 1], [1, 0]]": [[1.0, 1.0], [1.0, 0.0]],
    "leikkaus [[1, 1], [0, 1]]": [[1.0, 1.0], [0.0, 1.0]],
    "kierto 60°": [[math.cos(t), -math.sin(t)],
                   [math.sin(t), math.cos(t)]],
}
for nimi, a in matriisit.items():
    l1, l2 = ominaisarvot_2x2(a)
    print(f"{nimi:<29} λ = {teksti(l1)}, {teksti(l2)}")
    numpy = np.linalg.eigvals(np.array(a))
    assert np.allclose(sorted(numpy, key=lambda z: (z.real, z.imag)),
                       sorted([l1, l2], key=lambda z: (z.real, z.imag)))
# @loppu karakteristinen

# @alku jalki
# Ominaisarvojen summa on jälki ja tulo determinantti, kaikenkokoisille
# matriiseille.
A = np.array([[4.0, 1.0, 2.0], [0.0, 3.0, -1.0], [1.0, 0.0, 2.0]])
arvot = np.linalg.eigvals(A)
print("summa = jälki:", bool(np.isclose(arvot.sum(), np.trace(A))))
print("tulo = determinantti:",
      bool(np.isclose(np.prod(arvot), np.linalg.det(A))))
# Kierron ominaisarvot ovat e^(±iθ): itseisarvo 1, kulma kiertokulma.
l1, _ = ominaisarvot_2x2(matriisit["kierto 60°"])
print(f"kierto: |λ| = {abs(l1):.4f},",
      f"kulma {math.degrees(cmath.phase(l1)):.1f}°")
# @loppu jalki

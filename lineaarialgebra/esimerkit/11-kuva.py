"""Matala-asteinen approksimaatio: kuvan pakkaus singulaariarvoilla."""

import numpy as np
import numpy.typing as npt

Matriisi = npt.NDArray[np.float64]


# @alku kuva
def testikuva(n: int = 64) -> Matriisi:
    """Harmaasävykuva matriisina: liukuväri, kiekko ja suorakulmio."""
    y, x = np.mgrid[0:n, 0:n] / (n - 1)
    kuva = 0.25 + 0.5 * x
    kuva[(x - 0.35)**2 + (y - 0.4)**2 < 0.05] = 0.95
    kuva[(y > 0.72) & (y < 0.88) & (x > 0.45) & (x < 0.9)] = 0.05
    return np.asarray(kuva, dtype=np.float64)


def approksimaatio(u: Matriisi, s: Matriisi, vt: Matriisi,
                   k: int) -> Matriisi:
    """k suurinta singulaariarvoa: asteen k matriisi lähimpänä A:ta."""
    return (u[:, :k] * s[:k]) @ vt[:k]
# @loppu kuva


# @alku pakkaus
kuva = testikuva()
m, n = kuva.shape
U, s, Vt = np.linalg.svd(kuva, full_matrices=False)
print(f"kuva {m} × {n}, aste {np.linalg.matrix_rank(kuva)},",
      f"lukuja {m * n}")
print(" k  lukuja  osuus  suht. virhe")
for k in (1, 2, 4, 8, 16):
    ak = approksimaatio(U, s, Vt, k)
    virhe = np.linalg.norm(kuva - ak) / np.linalg.norm(kuva)
    lukuja = k * (m + n + 1)
    print(f"{k:>2}  {lukuja:>6}  {lukuja / (m * n):5.0%}  {virhe:.3f}")
# @loppu pakkaus

# @alku virhe
# Eckartin–Youngin lause: virhe on pois jätettyjen singulaariarvojen
# neliösumman neliöjuuri, eikä mikään asteen k matriisi ole lähempänä.
k = 4
a4 = approksimaatio(U, s, Vt, k)
print("virhe = sqrt(sum s_i^2, i > k):",
      bool(np.isclose(np.linalg.norm(kuva - a4), np.sqrt(np.sum(s[k:]**2)))))
print("approksimaation aste:", int(np.linalg.matrix_rank(a4)))
# @loppu virhe

"""LU, Cholesky, QR ja SVD SciPyllä: milloin mitäkin."""

import numpy as np
from scipy import linalg

rng = np.random.default_rng(2026)

# @alku lu
# Sama matriisi, monta oikeaa puolta: hajotelma kerran (n^3/3 kertolaskua),
# jokainen ratkaisu sen jälkeen n^2.
A = np.array([[2.0, 1.0, 1.0], [4.0, -6.0, 0.0], [-2.0, 7.0, 2.0]])
P, L, U = linalg.lu(A)                   # A = P L U
print("L =\n", np.round(L, 3), "\nU =\n", np.round(U, 3), sep="")
lu, piv = linalg.lu_factor(A)
for b in ([5.0, -2.0, 9.0], [1.0, 0.0, 0.0]):
    x = linalg.lu_solve((lu, piv), b)
    print("x =", np.round(x, 6))
# @loppu lu

# @alku cholesky
# Symmetrinen ja positiivisesti definiitti: A = L L^T, puolet LU:n työstä,
# ei tuentaa tarvita. Epäonnistuminen paljastaa, ettei matriisi ole PD.
M = rng.standard_normal((200, 200))
S = M @ M.T + 200 * np.eye(200)
c = linalg.cho_factor(S)
oikea_puoli = rng.standard_normal(200)
x = linalg.cho_solve(c, oikea_puoli)
print("Cholesky: suhteellinen jäännös < 1e-14:",
      bool(np.linalg.norm(S @ x - oikea_puoli)
           / np.linalg.norm(oikea_puoli) < 1e-14))
try:
    linalg.cholesky(np.array([[1.0, 2.0], [2.0, 1.0]]))
except linalg.LinAlgError:
    print("Cholesky hylkäsi indefiniitin matriisin")
# @loppu cholesky

# @alku svd
# SVD paljastaa lähes singulaarisen matriisin: pienin singulaariarvo
# suhteessa suurimpaan on ehtoluvun käänteisluku.
B = np.array([[1.0, 2.0], [1.0, 2.0 + 1e-10]])
s = linalg.svdvals(B)
print(f"singulaariarvot {s[0]:.3f} ja {s[1]:.0e}, "
      f"ehtoluku {s[0] / s[1]:.0e}")
# @loppu svd

"""Harva matriisi: 2D-Poissonin yhtälön diskretointi."""

import numpy as np
from scipy import sparse
from scipy.sparse import linalg as splinalg


# @alku poisson
def poisson2d(m: int) -> sparse.csr_array:
    """Viiden pisteen Laplace m x m -hilassa: n = m^2 tuntematonta,
    enintään viisi nollasta poikkeavaa alkiota riviä kohden."""
    T = sparse.diags_array([-1.0, 2.0, -1.0], offsets=[-1, 0, 1],
                           shape=(m, m))
    identiteetti = sparse.eye_array(m)
    return sparse.csr_array(sparse.kron(identiteetti, T)
                            + sparse.kron(T, identiteetti))
# @loppu poisson


# @alku koko
print("      n      nnz   tiheänä (Mt)  harvana (Mt)")
for m in (10, 100, 300):
    A = poisson2d(m)
    n = A.shape[0]
    tiheä_mt = n * n * 8 / 1e6
    harva_mt = (A.data.nbytes + A.indices.nbytes + A.indptr.nbytes) / 1e6
    print(f"{n:7d}  {A.nnz:7d}  {tiheä_mt:12.1f}  {harva_mt:12.2f}")
# @loppu koko

# @alku ratkaisu
A = poisson2d(100)
b = np.ones(A.shape[0]) / 101**2          # tasainen kuorma, h^2 = 1/101^2
u = splinalg.spsolve(A.tocsc(), b)        # suora harva LU (SuperLU)
print(f"spsolve: jäännös < 1e-12: "
      f"{bool(np.linalg.norm(A @ u - b) < 1e-12)}, "
      f"suurin taipuma {u.max():.5f}")
# @loppu ratkaisu

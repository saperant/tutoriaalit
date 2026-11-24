"""Iteratiiviset ratkaisijat: Jacobi, Gauss-Seidel ja liittogradientti."""

import math

import numpy as np
import numpy.typing as npt

Vektori = npt.NDArray[np.float64]
N = 30
TOL = 1e-8

# 1D-Poisson: A = tridiag(-1, 2, -1), symmetrinen ja positiivisesti
# definiitti, ehtoluku kasvaa kuten n^2.
A = 2 * np.eye(N) - np.eye(N, k=1) - np.eye(N, k=-1)
b = np.ones(N)


def jaannos(x: Vektori) -> float:
    return float(np.linalg.norm(b - A @ x) / np.linalg.norm(b))


# @alku jacobi
def jacobi() -> int:
    """x <- D^-1 (b - (A - D) x): kaikki komponentit vanhoista arvoista."""
    d = np.diag(A)
    x = np.zeros(N)
    for k in range(1, 100_000):
        x = x + (b - A @ x) / d
        if jaannos(x) < TOL:
            return k
    raise RuntimeError("ei suppene")


def gauss_seidel() -> int:
    """Kuten Jacobi, mutta uusia komponentteja käytetään heti."""
    x = np.zeros(N)
    for k in range(1, 100_000):
        for i in range(N):
            x[i] += (b[i] - A[i] @ x) / A[i, i]
        if jaannos(x) < TOL:
            return k
    raise RuntimeError("ei suppene")
# @loppu jacobi


# @alku cg
def liittogradientti() -> int:
    """CG: hakusuunnat ovat A-ortogonaalisia, joten tarkoilla luvuilla
    ratkaisu löytyy enintään N askeleessa."""
    x = np.zeros(N)
    r = b - A @ x
    p = r.copy()
    rr = float(r @ r)
    for k in range(1, 10 * N):
        Ap = A @ p
        alfa = rr / float(p @ Ap)
        x += alfa * p
        r -= alfa * Ap
        rr_uusi = float(r @ r)
        if math.sqrt(rr_uusi) / np.linalg.norm(b) < TOL:
            return k
        p = r + (rr_uusi / rr) * p
        rr = rr_uusi
    raise RuntimeError("ei suppene")
# @loppu cg


# @alku vertailu
rho = math.cos(math.pi / (N + 1))   # Jacobin iteraatiomatriisin spektrisäde
ennuste = math.log(TOL / math.sqrt(N)) / math.log(rho)
print(f"Jacobi:          {jacobi():5d} kierrosta "
      f"(ennuste spektrisäteestä ~{ennuste:.0f})")
print(f"Gauss-Seidel:    {gauss_seidel():5d} kierrosta "
      f"(ennuste ~{ennuste / 2:.0f})")
print(f"liittogradientti:{liittogradientti():5d} kierrosta "
      f"(enintään N = {N})")
# @loppu vertailu

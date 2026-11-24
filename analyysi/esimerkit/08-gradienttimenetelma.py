"""Gradienttimenetelmä: askel gradienttia vastaan kohti minimiä."""

import numpy as np
import numpy.typing as npt
from scipy import optimize

Vektori = npt.NDArray[np.float64]


# @alku menetelma
def f(p: Vektori) -> float:
    """Kustannus: (x - 1)^2 + 10 (y + 2)^2, minimi pisteessä (1, -2)."""
    return float((p[0] - 1) ** 2 + 10 * (p[1] + 2) ** 2)


def grad(p: Vektori) -> Vektori:
    return np.array([2 * (p[0] - 1), 20 * (p[1] + 2)])


def laskeudu(alku: Vektori, askel: float, kierroksia: int) -> Vektori:
    p = alku.copy()
    for _ in range(kierroksia):
        p = p - askel * grad(p)
    return p
# @loppu menetelma


# @alku askel
alku = np.array([5.0, 5.0])
for askel in (0.01, 0.05, 0.09, 0.11):
    p = laskeudu(alku, askel, 100)
    print(f"askel {askel}: piste ({p[0]:.4g}, {p[1]:.4g}), f = {f(p):.3g}")
# Suurin vakaa askel on 2/L, missä L = 20 on Hessen matriisin suurin
# ominaisarvo: y-suunnassa askel 0,11 ylittää rajan 0,1.
# @loppu askel

# @alku scipy
tulos = optimize.minimize(f, alku, jac=grad, method="BFGS")
print(f"BFGS: ({tulos.x[0]:.4f}, {tulos.x[1]:.4f}),"
      f" {tulos.nit} kierrosta")
# @loppu scipy

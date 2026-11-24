"""Rosenbrockin funktio: gradienttimenetelmä, Newton ja BFGS."""

import numpy as np
import numpy.typing as npt
from scipy import optimize

Vektori = npt.NDArray[np.float64]


# @alku rosenbrock
def f(v: Vektori) -> float:
    """Kapea kaareva laakso, minimi (1, 1)."""
    x, y = v
    return float((1 - x) ** 2 + 100 * (y - x * x) ** 2)


def gradientti(v: Vektori) -> Vektori:
    x, y = v
    return np.array([-2 * (1 - x) - 400 * x * (y - x * x),
                     200 * (y - x * x)])


def hessen(v: Vektori) -> Vektori:
    x, y = v
    return np.array([[2 - 400 * (y - 3 * x * x), -400 * x],
                     [-400 * x, 200.0]])
# @loppu rosenbrock


# @alku menetelmat
def gradienttimenetelma(v: Vektori, maks: int = 100_000) -> int:
    """Askel vastagradientin suuntaan; askelpituus puolitetaan, kunnes
    funktio pienenee riittävästi (Armijon ehto)."""
    for k in range(maks):
        g = gradientti(v)
        if np.linalg.norm(g) < 1e-6:
            return k
        t = 1.0
        while f(v - t * g) > f(v) - 1e-4 * t * float(g @ g):
            t /= 2
        v = v - t * g
    return maks


def newton(v: Vektori) -> int:
    """Newtonin askel ratkaisee H d = -g: neliöllinen paikallisesti."""
    for k in range(100):
        g = gradientti(v)
        if np.linalg.norm(g) < 1e-6:
            return k
        v = v + np.linalg.solve(hessen(v), -g)
    return 100
# @loppu menetelmat


# @alku vertailu
alku = np.array([-1.2, 1.0])
n = gradienttimenetelma(alku)
print(f"gradienttimenetelmä: yli 10 000 kierrosta: {n > 10_000}")
print(f"Newton:              {newton(alku)} kierrosta")
r = optimize.minimize(f, alku, jac=gradientti, method="BFGS",
                      options={"gtol": 1e-6})
print(f"BFGS: minimi ({r.x[0]:.6f}, {r.x[1]:.6f}), "
      f"alle 100 kierrosta: {r.nit < 100}")
# @loppu vertailu

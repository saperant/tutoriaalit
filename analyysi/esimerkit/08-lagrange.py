"""Rajoitettu optimointi Lagrangen kertojilla."""

import math

import numpy as np
import numpy.typing as npt
import sympy as sp
from scipy import optimize

Vektori = npt.NDArray[np.float64]

r, h, lam = sp.symbols("r h lambda", positive=True)

# @alku lagrange
# Tölkki uudelleen: minimoi A(r, h) ehdolla V(r, h) = 500.
# Optimissa gradientit ovat yhdensuuntaiset: grad A = lambda grad V.
A = 2 * sp.pi * r**2 + 2 * sp.pi * r * h
V = sp.pi * r**2 * h
L = A - lam * (V - 500)
yhtalot = [sp.diff(L, m) for m in (r, h, lam)]
ratkaisu = sp.solve(yhtalot, [r, h, lam], dict=True)[0]
print("r =", sp.N(ratkaisu[r], 4), "h =", sp.N(ratkaisu[h], 4),
      "lambda =", sp.N(ratkaisu[lam], 4))
print("h/r =", sp.simplify(ratkaisu[h] / ratkaisu[r]))
# @loppu lagrange

# @alku tulkinta
# Kertoja kertoo, paljonko optimin arvo muuttuu, kun rajoitus
# muuttuu yhden yksikön: dA*/dV = lambda.
A_opt = A.subs(ratkaisu)
print(f"dA/dV = lambda = {float(ratkaisu[lam]):.4f} cm^2/cm^3")
# @loppu tulkinta

# @alku scipy
# Numeerisesti: SLSQP hyväksyy yhtälörajoitteen.
def pinta(p: Vektori) -> float:
    return float(2 * math.pi * (p[0] ** 2 + p[0] * p[1]))


def tilavuusehto(p: Vektori) -> float:
    return float(math.pi * p[0] ** 2 * p[1] - 500)


tulos = optimize.minimize(pinta, x0=np.array([3.0, 10.0]), method="SLSQP",
                          constraints={"type": "eq", "fun": tilavuusehto})
print(f"SLSQP: r = {tulos.x[0]:.3f}, h = {tulos.x[1]:.3f},"
      f" A = {tulos.fun:.2f}, A* = {float(A_opt):.2f}")
# @loppu scipy

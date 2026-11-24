"""Tilaesitys ja ratkaisu matriisieksponentilla."""

import numpy as np
import sympy as sp
from scipy.linalg import expm

# @alku tila
# y'' + 5 y' + 4 y = 0. Tilamuuttujat x1 = y ja x2 = y', jolloin
# x' = A x, missä A = [[0, 1], [-4, -5]].
A = sp.Matrix([[0, 1], [-4, -5]])
print("ominaisarvot:", A.eigenvals())
for arvo, _kerta, vektorit in A.eigenvects():
    print(f"  lambda = {arvo}: v = {list(vektorit[0])}")
# @loppu tila

# @alku eksponentti
# Ratkaisu x(t) = exp(A t) x(0). SymPy laskee matriisieksponentin
# tarkasti, SciPy numeerisesti.
t = sp.symbols("t")
x0 = sp.Matrix([1, 0])
tarkka = sp.simplify((A * t).exp() * x0)
print("y(t) =", sp.expand(tarkka[0]))
numeerinen = expm(np.array(A, dtype=float) * 1.5) @ np.array([1.0, 0.0])
print(
    f"t = 1,5: SymPy {float(tarkka[0].subs(t, 1.5)):.10f}, "
    f"SciPy {numeerinen[0]:.10f}"
)
# @loppu eksponentti

# @alku dsolve
y = sp.Function("y")
vertailu = sp.dsolve(
    y(t).diff(t, 2) + 5 * y(t).diff(t) + 4 * y(t),
    y(t),
    ics={y(0): 1, y(t).diff(t).subs(t, 0): 0},
).rhs
print("dsolve sama:", sp.simplify(vertailu - tarkka[0]) == 0)
# @loppu dsolve

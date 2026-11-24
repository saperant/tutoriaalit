"""Pakotettu värähtely ja resonanssi."""

import math

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

t = sp.symbols("t", nonnegative=True)
w = sp.symbols("omega", positive=True)
y = sp.Function("y")

# @alku yksityis
# y'' + 0,4 y' + 4 y = cos(w t). Yksityisratkaisu yritteellä
# A cos(wt) + B sin(wt); amplitudi sqrt(A^2 + B^2).
A, B = sp.symbols("A B")
yrite = A * sp.cos(w * t) + B * sp.sin(w * t)
jaannos = sp.expand(
    yrite.diff(t, 2)
    + sp.Rational(2, 5) * yrite.diff(t)
    + 4 * yrite
    - sp.cos(w * t)
)
kertoimet = sp.solve(
    [jaannos.coeff(sp.cos(w * t)), jaannos.coeff(sp.sin(w * t))], [A, B]
)
nelio = sp.simplify(kertoimet[A] ** 2 + kertoimet[B] ** 2)
print("1/amplitudi^2 =", sp.expand(1 / nelio))
kaava = (4 - w**2) ** 2 + (sp.Rational(2, 5) * w) ** 2
print(
    "sama kuin (4 - w^2)^2 + (0,4 w)^2:", sp.simplify(1 / nelio - kaava) == 0
)
amplitudi = 1 / sp.sqrt(kaava)
# @loppu yksityis

# @alku resonanssi
# Amplitudi on suurin, kun nimittäjä on pienin.
huippu = sp.solve(sp.diff(kaava, w), w)
print("resonanssi w =", huippu, "~", [round(float(h), 4) for h in huippu])
for arvo in (1.0, 1.98, 3.0):
    print(f"w = {arvo:4.2f}: amplitudi {float(amplitudi.subs(w, arvo)):.4f}")
# @loppu resonanssi


# @alku numeerinen
# Simuloidaan resonanssitaajuudella: alkuvaihe vaimenee ja jäljelle jää
# jatkuvuustilan värähtely, jonka amplitudi vastaa kaavaa.
def f(s: float, z: np.ndarray, taaj: float = 1.98) -> np.ndarray:
    return np.array([z[1], math.cos(taaj * s) - 0.4 * z[1] - 4.0 * z[0]])


tulos = solve_ivp(f, (0.0, 60.0), [0.0, 0.0], max_step=0.01, rtol=1e-8)
loppu = tulos.y[0][tulos.t > 45.0]
print(f"simuloitu amplitudi: {(loppu.max() - loppu.min()) / 2:.4f}")
# @loppu numeerinen

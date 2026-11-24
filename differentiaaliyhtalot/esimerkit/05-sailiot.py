"""Kaksi säiliötä sarjassa: kytketty lineaarinen ryhmä."""

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

# @alku ryhma
# Säiliöön 1 (100 l) virtaa puhdasta vettä 10 l/min, sen ylivuoto
# säiliöön 2 (50 l) ja siitä ulos. Säiliössä 1 on alussa 5 kg suolaa.
# x1' = -(q/V1) x1,  x2' = (q/V1) x1 - (q/V2) x2.
q, V1, V2 = 10, 100, 50
A = sp.Matrix(
    [[-sp.Rational(q, V1), 0], [sp.Rational(q, V1), -sp.Rational(q, V2)]]
)
print("ominaisarvot:", sorted(A.eigenvals(), key=float))
t = sp.symbols("t", nonnegative=True)
x = sp.simplify((A * t).exp() * sp.Matrix([5, 0]))
print("x1(t) =", x[0])
print("x2(t) =", x[1])
# @loppu ryhma

# @alku huippu
# Toisen säiliön suolamäärä kasvaa ensin ja sitten laskee. Huippu on
# derivaatan nollakohdassa.
huippu = sp.solve(sp.diff(x[1], t), t)[0]
print(
    "huippu hetkellä",
    huippu,
    "=",
    round(float(huippu), 3),
    "min,",
    round(float(x[1].subs(t, huippu)), 4),
    "kg",
)
# @loppu huippu


# @alku numeerinen
def f(_t: float, z: np.ndarray) -> np.ndarray:
    tulos: np.ndarray = np.array(A, dtype=float) @ z
    return tulos


r = solve_ivp(
    f, (0, 30), [5.0, 0.0], t_eval=[float(huippu)], rtol=1e-10, atol=1e-12
)
print(f"solve_ivp samassa hetkessä: {r.y[1, 0]:.4f} kg")
# @loppu numeerinen

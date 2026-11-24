"""Jäähtyvä kahvi: sama malli symbolisesti, numeerisesti ja käsin."""

import math

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

# @alku malli
# Newtonin jäähtymislaki: lämpötilan muutosnopeus on verrannollinen
# lämpötilaeroon ympäristöön. k on jäähtymisvakio (1/min).
T_YMP = 21.0  # huoneen lämpötila (C)
T_ALKU = 90.0  # kahvi kaadettaessa (C)
K = 0.045  # jäähtymisvakio (1/min)
# @loppu malli

# @alku symbolinen
t, k, Ty, T0, Tj = sp.symbols("t k T_y T_0 T_j", positive=True)
T = sp.Function("T")
yhtalo = sp.Eq(T(t).diff(t), -k * (T(t) - Ty))
ratkaisu = sp.dsolve(yhtalo, T(t), ics={T(0): T0})
print("yleinen:", ratkaisu.rhs.expand())
# Milloin kahvi on juotavaa (T_j)? Ratkaistaan t yhtälöstä T(t) = T_j.
aika = sp.solve(sp.Eq(ratkaisu.rhs, Tj), t)[0]
print("aika:", sp.simplify(aika))
arvot = {k: K, Ty: T_YMP, T0: T_ALKU, Tj: 60}
print(f"60 C kohdalla: t = {float(aika.subs(arvot)):.2f} min")
# @loppu symbolinen


# @alku numeerinen
def oikea_puoli(_t: float, y: np.ndarray) -> np.ndarray:
    return -K * (y - T_YMP)


nume = solve_ivp(
    oikea_puoli,
    (0.0, 30.0),
    [T_ALKU],
    t_eval=[10.0, 20.0, 30.0],
    rtol=1e-9,
    atol=1e-9,
)
for ti, yi in zip(nume.t, nume.y[0], strict=True):
    tarkka = T_YMP + (T_ALKU - T_YMP) * math.exp(-K * ti)
    print(f"t = {ti:4.1f}: numeerinen {yi:.4f}, tarkka {tarkka:.4f}")
# @loppu numeerinen

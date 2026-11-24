"""Rajasykli: van der Polin oskillaattori."""

import numpy as np
from scipy.integrate import solve_ivp

MU = 1.0


# @alku vanderpol
# x'' - mu (1 - x^2) x' + x = 0. Pienellä amplitudilla vaimennus on
# negatiivinen (energiaa tulee lisää), suurella positiivinen. Tasapaino
# origossa on epästabiili, mutta radat eivät karkaa: ne kiertyvät kohti
# rajasykliä, jonka amplitudi on noin 2.
def f(_t: float, z: np.ndarray) -> np.ndarray:
    x, v = z
    return np.array([v, MU * (1 - x * x) * v - x])


for alku in ((0.01, 0.0), (1.0, 0.0), (4.0, 0.0)):
    r = solve_ivp(f, (0, 60), alku, max_step=0.01, rtol=1e-9, atol=1e-12)
    loppu = r.y[0][r.t > 40]
    print(f"alku x = {alku[0]:5.2f}: amplitudi lopussa {loppu.max():.3f}")
# @loppu vanderpol

# @alku jakso
# Jakso mitataan kahden peräkkäisen nousevan nollakohdan välisenä aikana.
r = solve_ivp(f, (0, 60), (1.0, 0.0), max_step=0.001, rtol=1e-10, atol=1e-12)
nousut = r.t[1:][(r.y[0][:-1] < 0) & (r.y[0][1:] >= 0)]
print(f"jakso: {nousut[-1] - nousut[-2]:.3f}")
# @loppu jakso

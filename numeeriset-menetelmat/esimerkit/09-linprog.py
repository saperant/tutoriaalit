"""Lineaarinen optimointi: tuotannon suunnittelu SciPyn linprogilla."""

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linprog, milp

# @alku malli
# Paja valmistaa pöytiä (x1) ja tuoleja (x2). Kate 120 e / pöytä ja
# 50 e / tuoli. Puuta on 400 kg (pöytä 30 kg, tuoli 10 kg) ja
# työaikaa 300 h (pöytä 15 h, tuoli 10 h); tuoleja myydään enintään 25.
# linprog minimoi, joten kate otetaan negatiivisena.
c = np.array([-120.0, -50.0])
A_ub = np.array([[30.0, 10.0],     # puu
                 [15.0, 10.0]])    # työ
b_ub = np.array([400.0, 300.0])
tulos = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None), (0, 25)],
                method="highs")
# @loppu malli

# @alku tulos
assert tulos.x is not None and tulos.fun is not None
x1, x2 = tulos.x
print(f"pöytiä {x1:.2f}, tuoleja {x2:.2f}, kate {-tulos.fun:.2f} e")
# Varjohinnat: kuinka paljon kate kasvaa, jos rajoitetta löysätään yhdellä.
puu, tyo = -tulos.ineqlin.marginals
print(f"varjohinnat: puu {puu:.2f} e/kg, työ {tyo:.2f} e/h")
# @loppu tulos

# @alku kokonaisluvut
# Puolikkaita pöytiä ei myydä: sama tehtävä kokonaislukuina (milp).
kokonais = milp(c, constraints=LinearConstraint(A_ub, ub=b_ub),
                integrality=[1, 1], bounds=Bounds([0, 0], [np.inf, 25]))
assert kokonais.x is not None and kokonais.fun is not None
k1, k2 = np.round(kokonais.x)
print(f"kokonaisluvuin: pöytiä {k1:.0f}, tuoleja {k2:.0f}, "
      f"kate {-kokonais.fun:.2f} e")
# @loppu kokonaisluvut

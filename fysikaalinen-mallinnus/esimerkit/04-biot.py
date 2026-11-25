"""Milloin kappaleen voi mallintaa yhtenä lämpötilana?

Teräslevy jäähtyy ilmassa tai vedessä. Koko profiilin ratkaiseva malli
(implisiittinen Euler, konvektioreuna) verrataan yhden lämpötilan
malliin, jossa levy on koko ajan tasalämpöinen."""

import math

import numpy as np
import numpy.typing as npt
from scipy.linalg import solve_banded

Taulukko = npt.NDArray[np.float64]

K, RHO_C = 45.0, 3.8e6          # teräs: W/(m K), J/(m³ K)
PUOLIKAS = 0.010                # levyn puolipaksuus L, m
T_ALKU, T_YMP = 200.0, 20.0
N = 50                          # kontrollitilavuuksia keskeltä pintaan


# @alku profiili
def jaahdyta(h: float, t_loppu: float, askelia: int) -> Taulukko:
    """Levyn puolikas: keskellä symmetria (ei vuota), pinnassa
    konvektio h (T_pinta - T_ymp). Palauttaa lämpötilat lopussa."""
    dx = PUOLIKAS / N
    dt = t_loppu / askelia
    f = K * dt / (RHO_C * dx * dx)
    # Pinnan tilavuus: johtuminen puolen välin läpi sarjassa konvektion
    # kanssa.
    g = dt / (RHO_C * dx) / (dx / (2.0 * K) + 1.0 / h)
    nauha = np.zeros((3, N))
    nauha[0, 1:] = -f
    nauha[2, :-1] = -f
    nauha[1, :] = 1.0 + 2.0 * f
    nauha[1, 0] = 1.0 + f                    # symmetriataso
    nauha[1, -1] = 1.0 + f + g               # pinta
    u = np.full(N, T_ALKU)
    for _ in range(askelia):
        b = u.copy()
        b[-1] += g * T_YMP
        u = solve_banded((1, 1), nauha, b)
    return u
# @loppu profiili


# @alku vertailu
print("jäähdytys   h W/(m²K)    Bi  aika s  keski °C  pinta °C  "
      "yksi lämpötila °C")
for nimi, h, t in (("ilma", 25.0, 600.0), ("öljy", 500.0, 60.0),
                   ("vesi", 5000.0, 10.0)):
    u = jaahdyta(h, t, 2000)
    biot = h * PUOLIKAS / K
    # Yhden lämpötilan malli: rho c L dT/dt = -h (T - T_ymp)
    yksi = T_YMP + (T_ALKU - T_YMP) * math.exp(-h * t / (RHO_C * PUOLIKAS))
    print(f"{nimi:9s} {h:11.0f} {biot:5.2f} {t:7.0f} {u[0]:9.1f} "
          f"{u[-1]:9.1f} {yksi:14.1f}")
# @loppu vertailu

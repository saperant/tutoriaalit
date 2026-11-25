"""Ilman jäähdyttämä tanko kahden kuuman seinän välissä: koko ketju
säilymislaista tarkistukseen yhdessä tiedostossa."""

import math

import numpy as np
import numpy.typing as npt
from scipy.linalg import solve_banded

Taulukko = npt.NDArray[np.float64]

# @alku malli
# Alumiinitanko: halkaisija 5 mm, pituus 100 mm, päät seinissä 100 °C.
K = 200.0          # lämmönjohtavuus, W/(m K)
H = 25.0           # lämmönsiirtokerroin ilmaan, W/(m² K)
D = 0.005          # halkaisija, m
PITUUS = 0.100     # m
T_SEINA, T_ILMA = 100.0, 20.0
M2 = 4.0 * H / (K * D)      # hP/(kA) pyöreälle tangolle, 1/m²


def tarkka(x: Taulukko) -> Taulukko:
    """Yhtälön u'' = m²(u - T_ilma) ratkaisu annetuilla reuna-arvoilla."""
    m = math.sqrt(M2)
    theta = np.cosh(m * (x - PITUUS / 2)) / math.cosh(m * PITUUS / 2)
    return T_ILMA + (T_SEINA - T_ILMA) * theta
# @loppu malli


# @alku ratkaisu
def ratkaise(n: int) -> tuple[Taulukko, Taulukko]:
    """n sisäpistettä; palauttaa pisteet ja lämpötilat reunoineen."""
    h = PITUUS / (n + 1)
    x = np.linspace(0.0, PITUUS, n + 2)
    # Pisteen i tase: (u[i-1] - 2u[i] + u[i+1])/h² - m²(u[i] - T_ilma) = 0
    nauha = np.zeros((3, n))
    nauha[0, 1:] = -1.0 / h**2                  # ylälävistäjä
    nauha[1, :] = 2.0 / h**2 + M2               # lävistäjä
    nauha[2, :-1] = -1.0 / h**2                 # alalävistäjä
    b = np.full(n, M2 * T_ILMA)
    b[0] += T_SEINA / h**2                      # tunnetut reuna-arvot
    b[-1] += T_SEINA / h**2
    u = np.full(n + 2, T_SEINA)
    u[1:-1] = solve_banded((1, 1), nauha, b)
    return x, u
# @loppu ratkaisu


# @alku tarkistus
print(" pisteitä  keskikohta °C   suurin virhe K   virheiden suhde")
edellinen = 0.0
for n in (3, 7, 15, 31, 63):
    x, u = ratkaise(n)
    virhe = float(np.max(np.abs(u - tarkka(x))))
    suhde = f"{edellinen / virhe:8.2f}" if edellinen else "       -"
    print(f"{n:9d} {u[(n + 1) // 2]:14.4f} {virhe:16.2e} {suhde:>17}")
    edellinen = virhe
print(f"tarkka keskikohta: {float(tarkka(np.array([PITUUS / 2]))[0]):.4f}")
# @loppu tarkistus

"""Eristetty pää: reunaehdon diskretointi määrää koko ratkaisun
kertaluvun. Jäähdytysripa, jonka tyvi on 100 °C ja kärki eristetty."""

import math

import numpy as np
import numpy.typing as npt
from scipy.linalg import solve_banded

Taulukko = npt.NDArray[np.float64]

M2 = 400.0                  # hP/(kA), 1/m²
PITUUS = 0.100              # m
T_TYVI, T_ILMA = 100.0, 20.0


def tarkka(x: Taulukko) -> Taulukko:
    m = math.sqrt(M2)
    return (T_ILMA + (T_TYVI - T_ILMA)
            * np.cosh(m * (PITUUS - x)) / math.cosh(m * PITUUS))


# @alku ripa
def ratkaise(n: int, tapa: str) -> tuple[Taulukko, Taulukko]:
    """Pisteet x_0..x_n; x_0 on tyvi (tunnettu), x_n eristetty kärki."""
    h = PITUUS / n
    x = np.linspace(0.0, PITUUS, n + 1)
    nauha = np.zeros((3, n))              # tuntemattomat u_1..u_n
    nauha[0, 1:] = -1.0 / h**2
    nauha[1, :] = 2.0 / h**2 + M2
    nauha[2, :-1] = -1.0 / h**2
    b = np.full(n, M2 * T_ILMA)
    b[0] += T_TYVI / h**2
    if tapa == "toispuoleinen":
        # u'(L) = 0 muodossa (u_n - u_(n-1))/h = 0: ensimmäinen kertaluku.
        nauha[1, -1], nauha[2, -2], b[-1] = 1.0, -1.0, 0.0
    else:
        # Haamupiste u_(n+1) = u_(n-1): kärjen yhtälössä naapuri
        # lasketaan kahdesti. Toinen kertaluku.
        nauha[2, -2] = -2.0 / h**2
    u = np.empty(n + 1)
    u[0] = T_TYVI
    u[1:] = solve_banded((1, 1), nauha, b)
    return x, u
# @loppu ripa


# @alku kertaluku
def virhe(n: int, tapa: str) -> float:
    x, u = ratkaise(n, tapa)
    return float(np.max(np.abs(u - tarkka(x))))


print("    n  toispuoleinen kertaluku     haamupiste kertaluku")
for n in (10, 20, 40, 80, 160):
    rivi = f"{n:5d}"
    for tapa in ("toispuoleinen", "haamupiste"):
        nyt = virhe(n, tapa)
        p = math.log2(virhe(n // 2, tapa) / nyt)
        rivi += f" {nyt:14.2e} {p:9.2f}"
    print(rivi)
# @loppu kertaluku

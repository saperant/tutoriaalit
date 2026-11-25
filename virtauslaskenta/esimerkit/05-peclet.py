"""Advektio ja diffuusio tasapainossa: u c' = D c'' välillä [0, 1].

Reuna-arvot c(0) = 0 ja c(1) = 1. Virtaus painaa profiilin oikeaa reunaa
vasten ohueksi rajakerrokseksi, jonka paksuus on D / u."""

import math

import numpy as np
import numpy.typing as npt
from scipy.linalg import solve_banded

Taulukko = npt.NDArray[np.float64]

# @alku tehtava
PECLET = 50.0         # u L / D


def tarkka(x: Taulukko) -> Taulukko:
    tulos: Taulukko = np.expm1(PECLET * x) / math.expm1(PECLET)
    return tulos


def ratkaise(n: int, kaavio: str) -> tuple[Taulukko, Taulukko]:
    """n väliä; yhtälö kerrottuna h²/D:llä. p on hilan Péclet'n luku."""
    h = 1.0 / n
    p = PECLET * h
    if kaavio == "keskeis":       # p (c[i+1] - c[i-1]) / 2
        vasen, keski, oikea = -1.0 - p / 2.0, 2.0, -1.0 + p / 2.0
    else:                         # vastavirta: p (c[i] - c[i-1])
        vasen, keski, oikea = -1.0 - p, 2.0 + p, -1.0
    nauha = np.zeros((3, n - 1))
    nauha[0, 1:] = oikea
    nauha[1, :] = keski
    nauha[2, :-1] = vasen
    b = np.zeros(n - 1)
    b[-1] = -oikea                # reuna-arvo c(1) = 1
    c = np.zeros(n + 1)
    c[-1] = 1.0
    c[1:-1] = solve_banded((1, 1), nauha, b)
    x: Taulukko = np.linspace(0.0, 1.0, n + 1)
    return x, c
# @loppu tehtava


# @alku vertailu
print("  välejä  hilan Pe   keskeis: pienin  virhe    vastavirta: virhe")
for n in (10, 20, 40, 80, 160, 320):
    x, kesk = ratkaise(n, "keskeis")
    _, vasta = ratkaise(n, "vastavirta")
    pienin = round(float(np.min(kesk)), 3) + 0.0
    print(f"{n:8d} {PECLET / n:9.2f} {pienin:16.3f}"
          f" {float(np.max(np.abs(kesk - tarkka(x)))):6.3f}"
          f" {float(np.max(np.abs(vasta - tarkka(x)))):18.3f}")
# @loppu vertailu

"""CFL-ehto: Courantin luku yli yhden räjäyttää ratkaisun.

Sama kieli kuin edellä. Kaavion korkeimman taajuuden kerroin askelta
kohden on 2c² - 1 + sqrt((2c² - 1)² - 1), kun c > 1."""

import math

import numpy as np
import numpy.typing as npt

Taulukko = npt.NDArray[np.float64]
N = 100


def simuloi(c: float, askelia: int) -> list[float]:
    """Palauttaa suurimman poikkeaman jokaisen askeleen jälkeen."""
    x = np.linspace(0.0, 1.0, N + 1)
    vanha: Taulukko = np.where(x < 0.3, x / 0.3, (1.0 - x) / 0.7) * 0.01
    u = vanha.copy()
    u[1:-1] += 0.5 * c * c * (vanha[2:] - 2.0 * vanha[1:-1] + vanha[:-2])
    suurin = []
    for _ in range(askelia):
        uusi = np.zeros_like(u)
        uusi[1:-1] = (2.0 * u[1:-1] - vanha[1:-1]
                      + c * c * (u[2:] - 2.0 * u[1:-1] + u[:-2]))
        u, vanha = uusi, u
        suurin.append(float(np.max(np.abs(u))))
    return suurin


# @alku koe
print("Courant  suurin |u| 300 askeleen jälkeen  kasvu/askel  ennuste")
for c in (0.99, 1.00, 1.01, 1.05, 1.20):
    suurin = simuloi(c, 300)
    if c > 1.0:
        a = 2.0 * c * c - 1.0
        ennuste = f"{a + math.sqrt(a * a - 1.0):8.3f}"
        mitattu = f"{(suurin[-1] / suurin[-51]) ** (1 / 50):11.3f}"
    else:
        ennuste, mitattu = "       -", "          -"
    print(f"{c:7.2f} {suurin[-1]:33.3e} {mitattu} {ennuste}")
# @loppu koe

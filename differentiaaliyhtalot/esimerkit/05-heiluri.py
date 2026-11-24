"""Epälineaarinen heiluri ja sen linearisointi."""

import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import ellipk

G_PER_L = 9.81  # g/L, kun varren pituus on 1 m


# @alku jakso
# theta'' = -(g/L) sin(theta). Pienillä kulmilla sin(theta) ~ theta,
# jolloin jaksonaika on 2 pi sqrt(L/g) amplitudista riippumatta.
# Tarkka jaksonaika on 4 sqrt(L/g) K(sin^2(theta0/2)).
def heiluri(_t: float, z: np.ndarray) -> np.ndarray:
    return np.array([z[1], -G_PER_L * math.sin(z[0])])


def nolla_ylospain(_t: float, z: np.ndarray) -> float:
    return float(z[1])  # kulmanopeus vaihtaa merkkiä ääriasennossa


nolla_ylospain.direction = 1  # type: ignore[attr-defined]

lineaarinen = 2 * math.pi / math.sqrt(G_PER_L)
print(f"linearisoitu jakso: {lineaarinen:.4f} s")
for asteet in (5, 30, 90, 170):
    th0 = math.radians(asteet)
    kaava = 4 / math.sqrt(G_PER_L) * float(ellipk(math.sin(th0 / 2) ** 2))
    sim = solve_ivp(
        heiluri,
        (0, 10),
        [th0, 0.0],
        events=nolla_ylospain,
        rtol=1e-10,
        atol=1e-12,
    )
    # Ensimmäinen tapahtuma on vastakkainen ääriasento: puolijakso.
    simuloitu = 2 * float(sim.t_events[0][0])
    virhe = 100 * (kaava - lineaarinen) / kaava
    print(
        f"{asteet:3d} astetta: tarkka {kaava:.4f} s, "
        f"simuloitu {simuloitu:.4f} s, linearisoinnin virhe {virhe:4.1f} %"
    )
# @loppu jakso

"""Ulokepalkki tasojännitystilassa vakiovenymäkolmioilla (CST).

Teräslatta 1000 x 100 x 10 mm on kiinni vasemmasta päästään, ja oikeaa
päätä kuormittaa 1 kN alaspäin. Taipumaa verrataan palkkiteoriaan."""

import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve

sys.path.insert(0, str(Path(__file__).resolve().parent / "07-pienfem"))
from pienfem import Taulukko, Verkko, elementti, suorakulmio  # noqa: E402

E_MODUULI, NU = 210e9, 0.3
PITUUS, KORKEUS, PAKSUUS = 1.0, 0.1, 0.01
VOIMA = 1000.0

# @alku materiaali
# Tasojännitystila: jännitys = D @ venymä, venymä = (e_xx, e_yy, g_xy).
D = E_MODUULI / (1.0 - NU**2) * np.array([[1.0, NU, 0.0],
                                          [NU, 1.0, 0.0],
                                          [0.0, 0.0, (1.0 - NU) / 2.0]])
# @loppu materiaali


# @alku elementti
def venymamatriisi(p: Taulukko) -> tuple[Taulukko, float]:
    """B (3 x 6): venymä = B @ (u0, v0, u1, v1, u2, v2). Lineaarisen
    kolmion venymä on vakio koko elementissä."""
    g, ala = elementti(p)             # kantafunktioiden gradientit
    b = np.zeros((3, 6))
    b[0, 0::2] = g[:, 0]              # e_xx = du/dx
    b[1, 1::2] = g[:, 1]              # e_yy = dv/dy
    b[2, 0::2] = g[:, 1]              # g_xy = du/dy + dv/dx
    b[2, 1::2] = g[:, 0]
    return b, ala


def jaykkyys(verkko: Verkko) -> sp.csr_array:
    rivit, sarakkeet, arvot = [], [], []
    for solmut in verkko.kolmiot:
        b, ala = venymamatriisi(verkko.pisteet[solmut])
        ke = PAKSUUS * ala * (b.T @ D @ b)
        vapaus = np.column_stack([2 * solmut, 2 * solmut + 1]).ravel()
        for i in range(6):
            for j in range(6):
                rivit.append(vapaus[i])
                sarakkeet.append(vapaus[j])
                arvot.append(ke[i, j])
    n = 2 * len(verkko.pisteet)
    return sp.coo_array((arvot, (rivit, sarakkeet)), shape=(n, n)).tocsr()
# @loppu elementti


# @alku ratkaisu
def taivuta(nx: int, ny: int) -> tuple[float, float, float]:
    """Palauttaa pään taipuman (m) sekä suurimman vetojännityksen (Pa)
    koko palkissa ja sen ulommassa puolikkaassa."""
    verkko = suorakulmio(nx, ny, PITUUS, KORKEUS)
    x = verkko.pisteet[:, 0]
    k = jaykkyys(verkko)
    f = np.zeros(2 * len(x))
    paa = np.flatnonzero(x > PITUUS - 1e-9)
    paino = np.full(len(paa), 1.0 / ny)       # tasainen leikkausvoima
    paino[[0, -1]] *= 0.5                     # kulmasolmuille puolet
    f[2 * paa + 1] = -VOIMA * paino
    kiinni = np.flatnonzero(x < 1e-9)
    lukitut = np.concatenate([2 * kiinni, 2 * kiinni + 1])
    vapaat = np.setdiff1d(np.arange(len(f)), lukitut)
    u = np.zeros(len(f))
    u[vapaat] = spsolve(k[vapaat][:, vapaat].tocsc(), f[vapaat])
    juuri = keski = 0.0
    for solmut in verkko.kolmiot:
        b, _ = venymamatriisi(verkko.pisteet[solmut])
        vapaus = np.column_stack([2 * solmut, 2 * solmut + 1]).ravel()
        sxx = float((D @ b @ u[vapaus])[0])       # vakio elementissä
        juuri = max(juuri, sxx)
        if x[solmut].min() > PITUUS / 2.0 - 1e-9:
            keski = max(keski, sxx)
    return float(-u[2 * paa + 1].mean()), juuri, keski
# @loppu ratkaisu


# @alku vertailu
hitaus = PAKSUUS * KORKEUS**3 / 12.0
liukumoduuli = E_MODUULI / (2.0 * (1.0 + NU))
teoria = (VOIMA * PITUUS**3 / (3.0 * E_MODUULI * hitaus)
          + VOIMA * PITUUS / (5.0 / 6.0 * liukumoduuli * PAKSUUS * KORKEUS))
teoria_juuri = VOIMA * PITUUS * (KORKEUS / 2.0) / hitaus
print(f"palkkiteoria: taipuma {1e3 * teoria:.4f} mm, jännitys juuressa "
      f"{1e-6 * teoria_juuri:.1f} MPa ja keskellä "
      f"{0.5e-6 * teoria_juuri:.1f} MPa")
print("   verkko  vapausasteita  taipuma mm  osuus %  juuri MPa  keski MPa")
for nx, ny in ((10, 1), (20, 2), (40, 4), (80, 8), (160, 16)):
    taipuma, juuri, keski = taivuta(nx, ny)
    print(f"{nx:4d} x {ny:<2d} {2 * (nx + 1) * (ny + 1):13d} "
          f"{1e3 * taipuma:11.4f} {100.0 * taipuma / teoria:8.1f} "
          f"{1e-6 * juuri:10.1f} {1e-6 * keski:10.1f}")
# @loppu vertailu

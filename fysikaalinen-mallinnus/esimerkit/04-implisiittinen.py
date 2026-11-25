"""Implisiittinen Euler ja Crank–Nicolson lämpöyhtälölle.

Theta-menetelmä: (I + theta r A) u_uusi = (I - (1 - theta) r A) u_vanha,
jossa A on toisen differenssin matriisi tridiag(-1, 2, -1)."""

import math

import numpy as np
import numpy.typing as npt
from scipy.linalg import solve_banded

Taulukko = npt.NDArray[np.float64]


# @alku theta
def theta_askel(u: Taulukko, r: float, theta: float) -> Taulukko:
    """Yksi askel sisäpisteille; reuna-arvot ovat nollia."""
    n = len(u)
    oikea = u.copy()
    e = (1.0 - theta) * r
    oikea[1:] += e * u[:-1]
    oikea[:-1] += e * u[1:]
    oikea -= 2.0 * e * u
    nauha = np.zeros((3, n))
    nauha[0, 1:] = -theta * r
    nauha[1, :] = 1.0 + 2.0 * theta * r
    nauha[2, :-1] = -theta * r
    uusi: Taulukko = solve_banded((1, 1), nauha, oikea)
    return uusi
# @loppu theta


# @alku kertaluku
def virhe_ajassa(askelia: int, theta: float, valeja: int = 2000) -> float:
    """Sinialkutila hetkeen 0,1; hila on niin tiheä, että aikavirhe
    hallitsee."""
    x = np.linspace(0.0, 1.0, valeja + 1)[1:-1]
    dt = 0.1 / askelia
    u = np.sin(math.pi * x)
    for _ in range(askelia):
        u = theta_askel(u, dt * valeja**2, theta)
    tarkka = math.exp(-math.pi**2 * 0.1) * np.sin(math.pi * x)
    return float(np.max(np.abs(u - tarkka)))


print("askelia  impl. Euler  kertaluku  Crank–Nicolson  kertaluku")
ed_e = ed_c = 0.0
for askelia in (5, 10, 20, 40):
    e, c = virhe_ajassa(askelia, 1.0), virhe_ajassa(askelia, 0.5)
    pe = f"{math.log2(ed_e / e):9.2f}" if ed_e else "        -"
    pc = f"{math.log2(ed_c / c):9.2f}" if ed_c else "        -"
    print(f"{askelia:7d} {e:12.2e} {pe} {c:15.2e} {pc}")
    ed_e, ed_c = e, c
# @loppu kertaluku

# @alku porras
# Epäjatkuva alkutila ja pitkä askel: tangon keskiosa on 1, muu 0.
# Lämpöyhtälö ei luo uusia huippuja: profiilissa saa olla yksi ääriarvo.
def aariarvoja(u: Taulukko) -> int:
    muutos = np.diff(u)
    return int(np.sum(muutos[1:] * muutos[:-1] < 0.0))


valeja = 100
x = np.linspace(0.0, 1.0, valeja + 1)[1:-1]
alku = np.where(np.abs(x - 0.5) < 0.1, 1.0, 0.0)
r = 20.0                                  # 40 kertaa eksplisiittinen raja
print(f"\nporrasalkutila, r = {r:.0f}: paikallisia ääriarvoja askelittain")
for nimi, theta in (("impl. Euler", 1.0), ("Crank–Nicolson", 0.5)):
    u = alku.copy()
    maarat = []
    for _ in range(4):
        u = theta_askel(u, r, theta)
        maarat.append(aariarvoja(u))
    print(f"{nimi:15s} {maarat}  huippu {float(u.max()):.3f}")
# @loppu porras

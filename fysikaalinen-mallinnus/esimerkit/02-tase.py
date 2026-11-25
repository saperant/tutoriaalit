"""Energiatase kahden aineen tangossa: säilyvä ja säilymätön diskretointi.

Tangon vasenta päätä lämmitetään vakioteholla, muut pinnat on eristetty.
Kaiken syötetyn energian pitää löytyä tangosta."""

import numpy as np
import numpy.typing as npt

Taulukko = npt.NDArray[np.float64]

# @alku tanko
N = 40                       # kontrollitilavuuksia
DX = 0.200 / N               # tangon pituus 200 mm
ALA = 1.0e-4                 # poikkipinta 1 cm²
TEHO = 2.0                   # W vasempaan päähän
# Vasen puolisko kuparia, oikea terästä: k W/(m K), rho*c J/(m³ K).
K: Taulukko = np.where(np.arange(N) < N // 2, 390.0, 45.0)
RHO_C: Taulukko = np.where(np.arange(N) < N // 2, 3.4e6, 3.8e6)
DT = 0.02                    # s
# @loppu tanko


# @alku sailyva
def askel_sailyva(u: Taulukko) -> Taulukko:
    """Jokainen tilavuus saa sen, minkä naapuri luovuttaa."""
    # Rajapinnan johtavuus: kahden puolikkaan sarjaankytkentä.
    k_raja = 2.0 * K[:-1] * K[1:] / (K[:-1] + K[1:])
    vuo = np.zeros(N + 1)                       # W/m², positiivinen oikealle
    vuo[0] = TEHO / ALA                         # lämmitys
    vuo[1:-1] = -k_raja * (u[1:] - u[:-1]) / DX
    vuo[-1] = 0.0                               # eristetty pää
    return u + DT * (vuo[:-1] - vuo[1:]) / (RHO_C * DX)
# @loppu sailyva


# @alku sailymaton
def askel_sailymaton(u: Taulukko) -> Taulukko:
    """Sama yhtälö auki kerrottuna: k u'' + k' u'. Derivaatat
    keskeisdifferensseinä; reunoilla sama haamupiste kuin yllä."""
    laaj = np.concatenate(([u[0] + TEHO / ALA * DX / K[0]], u, [u[-1]]))
    k_laaj = np.concatenate(([K[0]], K, [K[-1]]))
    u2 = (laaj[2:] - 2.0 * laaj[1:-1] + laaj[:-2]) / DX**2
    u1 = (laaj[2:] - laaj[:-2]) / (2.0 * DX)
    k1 = (k_laaj[2:] - k_laaj[:-2]) / (2.0 * DX)
    return u + DT * (K * u2 + k1 * u1) / RHO_C
# @loppu sailymaton


def energia(u: Taulukko) -> float:
    """Tankoon varastoitunut energia alkutilaan (0 °C) verrattuna, J."""
    return float(np.sum(RHO_C * u) * DX * ALA)


# @alku ajo
print("  aika s  syötetty J   säilyvä J  säilymätön J  kuparin pää °C")
a = np.zeros(N)
b = np.zeros(N)
for kierros in range(1, 30001):
    a, b = askel_sailyva(a), askel_sailymaton(b)
    if kierros % 7500 == 0:
        t = kierros * DT
        print(f"{t:8.0f} {TEHO * t:11.2f} {energia(a):11.2f} "
              f"{energia(b):13.2f} {a[0]:15.2f}")
# @loppu ajo

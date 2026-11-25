"""Kaksikerroksinen seinä: rajapinnan johtavuus ratkaisee.

Tiili 130 mm ja mineraalivilla 100 mm, sisällä 21 °C ja ulkona -15 °C.
Stationaarinen lämpövirta tunnetaan lämpövastusten sarjaankytkennästä."""

import numpy as np
import numpy.typing as npt
from scipy.linalg import solve_banded

Taulukko = npt.NDArray[np.float64]

L_TIILI, K_TIILI = 0.130, 0.60       # m, W/(m K)
L_VILLA, K_VILLA = 0.100, 0.036
T_SISA, T_ULKO = 21.0, -15.0
PITUUS = L_TIILI + L_VILLA


# @alku kokoaminen
def ratkaise(n: int, keskiarvo: str) -> tuple[Taulukko, float]:
    """n kontrollitilavuutta; palauttaa lämpötilat ja lämpövuon W/m²."""
    dx = PITUUS / n
    keskipisteet = (np.arange(n) + 0.5) * dx
    k: Taulukko = np.where(keskipisteet < L_TIILI, K_TIILI, K_VILLA)
    if keskiarvo == "harmoninen":       # vastukset sarjassa
        k_raja = 2.0 * k[:-1] * k[1:] / (k[:-1] + k[1:])
    else:                               # aritmeettinen
        k_raja = 0.5 * (k[:-1] + k[1:])
    # Reunatilavuuden keskipiste on puolen välin päässä pinnasta.
    vasen, oikea = 2.0 * k[0], 2.0 * k[-1]
    nauha = np.zeros((3, n))
    nauha[0, 1:] = -k_raja
    nauha[2, :-1] = -k_raja
    nauha[1, :] = (np.concatenate(([vasen], k_raja))
                   + np.concatenate((k_raja, [oikea])))
    b = np.zeros(n)
    b[0], b[-1] = vasen * T_SISA, oikea * T_ULKO
    u: Taulukko = solve_banded((1, 1), nauha, b)
    vuo = vasen * (T_SISA - u[0]) / dx
    return u, float(vuo)
# @loppu kokoaminen


# @alku vertailu
vastus = L_TIILI / K_TIILI + L_VILLA / K_VILLA          # m² K / W
tarkka_vuo = (T_SISA - T_ULKO) / vastus
t_raja = T_SISA - tarkka_vuo * L_TIILI / K_TIILI
print(f"vastusmalli: vuo {tarkka_vuo:.3f} W/m², rajapinta {t_raja:.2f} °C")
print("tilavuuksia  harmoninen W/m²  aritmeettinen W/m²")
for n in (23, 46, 92, 230):          # rajapinta osuu tilavuuksien väliin
    _, h = ratkaise(n, "harmoninen")
    _, a = ratkaise(n, "aritmeettinen")
    print(f"{n:11d} {h:16.3f} {a:19.3f}")
# @loppu vertailu

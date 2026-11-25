"""Eksplisiittinen lämpöyhtälön ratkaisija ja sen stabiilisuusraja.

Tanko (pituus 1, alfa 1), päät 0. Alkutila on sinin puolikas, jolle
tarkka ratkaisu on exp(-pi² t) sin(pi x), ja lisäksi pieni häiriö, joka
edustaa pyöristys- ja mittausvirheitä."""

import math

import numpy as np
import numpy.typing as npt

Taulukko = npt.NDArray[np.float64]
N = 50                          # välejä; h = 1/N
T_LOPPU = 0.1


# @alku askel
def ftcs(u: Taulukko, r: float) -> Taulukko:
    """Yksi aika-askel; r = alfa dt / h². Reunapisteet pysyvät nollina."""
    uusi = u.copy()
    uusi[1:-1] = u[1:-1] + r * (u[2:] - 2.0 * u[1:-1] + u[:-2])
    return uusi
# @loppu askel


# @alku koe
x = np.linspace(0.0, 1.0, N + 1)
hairio = 1e-6 * (-1.0) ** np.arange(N + 1)      # sahalaita, korkein taajuus
hairio[0] = hairio[-1] = 0.0
print("     r  askelia  suurin |u|   virhe      suurin kerroin |1 - 4r|")
for r in (0.25, 0.45, 0.50, 0.51, 0.55):
    dt = r / N**2
    askelia = round(T_LOPPU / dt)
    u = np.sin(math.pi * x) + hairio
    for _ in range(askelia):
        u = ftcs(u, r)
    tarkka = math.exp(-math.pi**2 * askelia * dt) * np.sin(math.pi * x)
    virhe = float(np.max(np.abs(u - tarkka)))
    print(f"{r:6.2f} {askelia:8d} {float(np.max(np.abs(u))):11.3e} "
          f"{virhe:9.1e} {abs(1.0 - 4.0 * r):12.2f}")
# @loppu koe

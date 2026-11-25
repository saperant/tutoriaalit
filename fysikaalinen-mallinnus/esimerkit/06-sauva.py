"""Suippeneva vetosauva elementtimenetelmällä: elementtimatriisi,
kokoaminen ja reunaehdot näkyvissä silmukoina.

Terässauva on kiinni yläpäästään, ja alapäässä riippuu kuorma.
Poikkipinta pienenee lineaarisesti puoleen."""

import math

import numpy as np
import numpy.typing as npt

Taulukko = npt.NDArray[np.float64]

E_MODUULI = 210e9            # Pa
ALA0 = 4.0e-4                # m², yläpää (20 mm x 20 mm)
PITUUS = 2.0                 # m
VOIMA = 20e3                 # N alapäässä


def ala(x: float) -> float:
    return ALA0 * (1.0 - x / (2.0 * PITUUS))


def tarkka_siirtyma(x: float) -> float:
    """u(x) = F/E kertaa integraali dx/A(x)."""
    return (2.0 * VOIMA * PITUUS / (E_MODUULI * ALA0)
            * math.log(1.0 / (1.0 - x / (2.0 * PITUUS))))


# @alku kokoaminen
def kokoa(solmut: Taulukko) -> tuple[Taulukko, Taulukko]:
    """Jäykkyysmatriisi K ja kuormavektori f koko sauvalle."""
    n = len(solmut)
    k = np.zeros((n, n))
    f = np.zeros(n)
    for e in range(n - 1):                    # elementti solmujen e, e+1
        h = solmut[e + 1] - solmut[e]
        keski = 0.5 * (solmut[e] + solmut[e + 1])
        # Elementin jäykkyys: jousi, jonka vakio on EA/h.
        ke = E_MODUULI * ala(keski) / h * np.array([[1.0, -1.0],
                                                    [-1.0, 1.0]])
        for a in range(2):                    # paikallinen -> globaali
            for b in range(2):
                k[e + a, e + b] += ke[a, b]
    f[-1] = VOIMA                             # luonnollinen reunaehto
    return k, f
# @loppu kokoaminen


# @alku ratkaisu
def ratkaise(solmut: Taulukko) -> Taulukko:
    k, f = kokoa(solmut)
    u = np.zeros(len(solmut))
    # Oleellinen reunaehto u(0) = 0: solmu 0 pois yhtälöistä.
    u[1:] = np.linalg.solve(k[1:, 1:], f[1:])
    return u
# @loppu ratkaisu


# @alku tulos
print("elementtejä  pään siirtymä mm  virhe %   suurin jännitys MPa")
for n in (1, 2, 4, 8, 16):
    solmut = np.linspace(0.0, PITUUS, n + 1)
    u = ratkaise(solmut)
    jannitys = E_MODUULI * np.diff(u) / np.diff(solmut)   # vakio / elem.
    virhe = 100.0 * (u[-1] / tarkka_siirtyma(PITUUS) - 1.0)
    print(f"{n:11d} {1e3 * u[-1]:17.5f} {virhe:8.3f} "
          f"{1e-6 * float(jannitys.max()):21.2f}")
print(f"tarkka: siirtymä {1e3 * tarkka_siirtyma(PITUUS):.5f} mm, "
      f"jännitys alapäässä {1e-6 * VOIMA / ala(PITUUS):.2f} MPa")
# @loppu tulos

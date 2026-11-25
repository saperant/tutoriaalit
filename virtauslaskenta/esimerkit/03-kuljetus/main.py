"""Savuvana tasaisessa tuulessa: kontrollitilavuuksien tase ja vertailu
tunnettuun ratkaisuun."""

import math

import numpy as np

from kuljetus import Hila, Taulukko, ratkaise, tasainen_tuuli, ulosvirtaus

# @alku tehtava
TUULI = 1.0          # m/s, oikealle
DIFFUUSIO = 0.002    # m²/s
PAASTO = 1.0         # lähteen voimakkuus syvyysyksikköä kohden
LAHDE_X = 0.2        # lähteen paikka; korkeus on alueen puoliväli


def savuvana(nx: int, kaavio: str = "vastavirta"
             ) -> tuple[Hila, Taulukko, float]:
    """Alue 2 x 1; palauttaa hilan, pitoisuuden ja ulos virtaavan määrän."""
    hila = Hila(nx, nx // 2, 2.0 / nx)
    u, v = tasainen_tuuli(hila, TUULI, 0.0)
    lahde = np.zeros((hila.nx, hila.ny))
    lahde[round(LAHDE_X / hila.h), hila.ny // 2] = PAASTO
    c = ratkaise(hila, u, v, DIFFUUSIO, kaavio, lahde)
    return hila, c, ulosvirtaus(hila, u, v, c, DIFFUUSIO)
# @loppu tehtava


# @alku leveys
def vanan_leveys(hila: Hila, c: Taulukko, x: float) -> float:
    """Poikkileikkauksen keskihajonta kohdassa x."""
    _, y = hila.keskipisteet()
    sarake = c[round(x / hila.h - 0.5), :]
    keski = float(np.sum(sarake * y) / np.sum(sarake))
    hajonta2 = float(np.sum(sarake * (y - keski) ** 2) / np.sum(sarake))
    return math.sqrt(hajonta2)


def teoria(x: float) -> float:
    """Pistelähteen vana, kun tuuli kuljettaa paljon nopeammin kuin
    diffuusio levittää: sigma² = 2 D (x - x0) / U."""
    return math.sqrt(2.0 * DIFFUUSIO * (x - LAHDE_X) / TUULI)
# @loppu leveys


# @alku ajo
if __name__ == "__main__":
    print("ruutuja    h      tase   leveys x=1,0  x=1,6"
          "   teoria x=1,0  x=1,6")
    for nx in (40, 80, 160):
        hila, c, ulos = savuvana(nx)
        tase = "toteutuu" if abs(ulos - PAASTO) < 1e-9 else "EI TOTEUDU"
        print(f"{nx * nx // 2:7d} {hila.h:6.4f} {tase:>9}"
              f" {vanan_leveys(hila, c, 1.0):10.4f}"
              f" {vanan_leveys(hila, c, 1.6):7.4f}"
              f" {teoria(1.0):10.4f} {teoria(1.6):7.4f}")
    hila, c, _ = savuvana(80)
    print(f"pienin pitoisuus {round(float(np.min(c)), 3) + 0.0:.3f}")
# @loppu ajo

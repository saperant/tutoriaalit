"""Väärä diffuusio: sama savuvana, kun tuuli on vinossa hilaan nähden.

Vastavirtakaavio levittää ainetta kummankin koordinaattiakselin suuntaan
kertoimilla u h / 2 ja v h / 2. Kun virtaus on vinossa, osa tästä
levityksestä on virtausta vastaan kohtisuoraa, ja vana levenee
enemmän kuin fysiikka sallii."""

import math
import sys
from pathlib import Path

import numpy as np

# Luvun 3 kirjasto on viereisessä hakemistossa.
sys.path.insert(0, str(Path(__file__).resolve().parent / "03-kuljetus"))
from kuljetus import Hila, Taulukko, ratkaise, tasainen_tuuli  # noqa: E402

# @alku tehtava
TUULI = 1.0
DIFFUUSIO = 0.002
LAHDE = 0.15          # lähteen x- ja y-koordinaatti
MATKA = 0.6           # mittauskohdan etäisyys lähteestä virtaussuuntaan


def vana(n: int, kulma: float, kaavio: str) -> tuple[Hila, Taulukko]:
    """Yksikköneliö, n x n ruutua, tuulen suunta asteina x-akselista."""
    hila = Hila(n, n, 1.0 / n)
    a = math.radians(kulma)
    u, v = tasainen_tuuli(hila, TUULI * math.cos(a), TUULI * math.sin(a))
    lahde = np.zeros((n, n))
    lahde[round(LAHDE * n), round(LAHDE * n)] = 1.0
    return hila, ratkaise(hila, u, v, DIFFUUSIO, kaavio, lahde)
# @loppu tehtava


# @alku leveys
def leveys(hila: Hila, c: Taulukko, kulma: float) -> float:
    """Vanan keskihajonta virtausta vastaan kohtisuorassa suunnassa
    kaistalla, joka on etäisyydellä MATKA lähteestä."""
    a = math.radians(kulma)
    x, y = hila.keskipisteet()
    x0 = (round(LAHDE * hila.nx) + 0.5) * hila.h
    dx, dy = x[:, None] - x0, y[None, :] - x0
    pitkin = dx * math.cos(a) + dy * math.sin(a)
    poikki = -dx * math.sin(a) + dy * math.cos(a)
    kaista = np.abs(pitkin - MATKA) < hila.h
    paino = c[kaista]
    keski = float(np.sum(paino * poikki[kaista]) / np.sum(paino))
    return math.sqrt(float(np.sum(paino * (poikki[kaista] - keski) ** 2)
                           / np.sum(paino)))


def ennuste(h: float, kulma: float) -> float:
    """Leveys, kun fysikaaliseen diffuusioon lisätään vastavirtakaavion
    poikittainen osuus (U h / 2) sin a cos a (sin a + cos a)."""
    a = math.radians(kulma)
    vaara = (0.5 * TUULI * h * math.sin(a) * math.cos(a)
             * (math.sin(a) + math.cos(a)))
    return math.sqrt(2.0 * (DIFFUUSIO + vaara) * MATKA / TUULI)
# @loppu leveys


# @alku ajo
if __name__ == "__main__":
    oikea = math.sqrt(2.0 * DIFFUUSIO * MATKA / TUULI)
    print(f"fysikaalinen leveys {oikea:.4f}")
    print("ruutuja/sivu  kulma  laskettu  ennuste  väärä D / oikea D")
    for n, kulma in ((80, 0.0), (80, 15.0), (80, 30.0), (80, 45.0),
                     (160, 45.0), (320, 45.0)):
        hila, c = vana(n, kulma, "vastavirta")
        s = leveys(hila, c, kulma)
        suhde = (s / oikea) ** 2 - 1.0
        print(f"{n:12d} {kulma:6.1f} {s:9.4f} {ennuste(hila.h, kulma):8.4f}"
              f" {suhde:12.2f}")
    hila, c = vana(80, 45.0, "keskeis")
    print(f"keskeisdifferenssi, 80 ruutua, 45 astetta: leveys "
          f"{leveys(hila, c, 45.0):.4f}, pienin pitoisuus "
          f"{float(np.min(c)):.2f}")
# @loppu ajo

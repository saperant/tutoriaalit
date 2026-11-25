"""Pienet päivitykset matalalla tarkkuudella neljällä pyöristystavalla."""

import math
import random
from collections.abc import Callable

Pyoristys = Callable[[float], float]
rng = random.Random(2026)                 # kiinteä siemen: toistettava


def stokastinen(x: float, askel: float) -> float:
    """Sama kuin esimerkissä 09-stokastinen.py."""
    alempi = math.floor(x / askel)
    return (alempi + (rng.random() < x / askel - alempi)) * askel


def lahimpaan(x: float, askel: float) -> float:
    return round(x / askel) * askel


def katkaisu(x: float, askel: float) -> float:
    """Kiinteän pilkun luvun alimmat bitit pudotetaan pois."""
    return math.floor(x / askel) * askel


# @alku paivitys
ASKEL = 2.0 ** -8          # painon tarkkuus: kahdeksan murtobittiä
NOPEUS = 2.0 ** -6         # oppimisnopeus
TAVOITE = 0.7              # häviön (w - 0,7)^2 / 2 minimi


def opeta(askelia: int, pyorista: Pyoristys) -> list[float]:
    """Gradienttimenetelmä, jossa paino pyöristetään joka askeleella."""
    w, polku = 0.0, [0.0]
    for _ in range(askelia):
        w = pyorista(w - NOPEUS * (w - TAVOITE))
        polku.append(w)
    return polku


TAVAT: dict[str, Pyoristys] = {
    "tarkka": lambda w: w,
    "katkaisu": lambda w: katkaisu(w, ASKEL),
    "lähimpään": lambda w: lahimpaan(w, ASKEL),
    "stokastinen": lambda w: stokastinen(w, ASKEL),
}
# @loppu paivitys

print(f"tavoite {TAVOITE}, askel {ASKEL:.5f}")
POLUT = {nimi: opeta(600, tapa) for nimi, tapa in TAVAT.items()}
for nimi, polku in POLUT.items():
    loppu = polku[-200:]                  # viimeiset 200 askelta
    print(f"{nimi:12} loppuarvo {polku[-1]:.4f}  "
          f"keskiarvo {sum(loppu) / len(loppu):.4f}")

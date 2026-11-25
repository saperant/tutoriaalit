"""Seinän viereisen ruudun korkeus turbulentissa virtauksessa.

Seinän lähellä nopeus skaalautuu kitkanopeudella u_tau ja etäisyys
suureella y+ = y u_tau / nu. Hilan ensimmäisen ruudun y+ ratkaisee,
voiko turbulenssimalli laskea rajakerroksen seinään asti (y+ noin 1) vai
tarvitaanko seinäfunktio (y+ noin 30–300)."""

import math
from dataclasses import dataclass


# @alku seina
@dataclass(frozen=True)
class Tapaus:
    nimi: str
    nopeus: float      # m/s
    pituus: float      # m
    nu: float          # m²/s


def kitkanopeus(t: Tapaus) -> float:
    """Tasolevyn turbulentin rajakerroksen kokeellinen kitkakerroin
    c_f = 0,058 Re^(-1/5); arvio, joka riittää hilan mitoitukseen."""
    reynolds = t.nopeus * t.pituus / t.nu
    kitkakerroin = 0.058 * reynolds ** -0.2
    return t.nopeus * math.sqrt(kitkakerroin / 2.0)


def ruudun_korkeus(t: Tapaus, y_plus: float) -> float:
    """Ensimmäisen ruudun keskipisteen etäisyys seinästä."""
    return y_plus * t.nu / kitkanopeus(t)
# @loppu seina


# @alku taulukko
TAPAUKSET = (
    Tapaus("vesiputki, 50 mm", 2.0, 0.05, 1.0e-6),
    Tapaus("henkilöauto", 28.0, 4.5, 1.5e-5),
    Tapaus("matkustajakoneen siipi", 230.0, 5.0, 3.5e-5),
)

print(f"{'tapaus':24s} {'Re':>8s}  u_tau m/s   y+ = 1     y+ = 50")
for t in TAPAUKSET:
    reynolds = t.nopeus * t.pituus / t.nu
    print(f"{t.nimi:24s} {reynolds:8.1e} {kitkanopeus(t):10.3f}"
          f" {1e6 * ruudun_korkeus(t, 1.0):6.1f} µm"
          f" {1e3 * ruudun_korkeus(t, 50.0):7.2f} mm")
# @loppu taulukko

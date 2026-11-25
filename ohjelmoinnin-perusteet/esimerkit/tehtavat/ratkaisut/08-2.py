"""Malliratkaisu 08-2: Suorakulmio dataluokkana."""

from dataclasses import dataclass


@dataclass
class Suorakulmio:
    """Suorakulmio, jolla on leveys ja korkeus."""

    leveys: float
    korkeus: float

    def pinta_ala(self) -> float:
        return self.leveys * self.korkeus

    def on_nelio(self) -> bool:
        return self.leveys == self.korkeus

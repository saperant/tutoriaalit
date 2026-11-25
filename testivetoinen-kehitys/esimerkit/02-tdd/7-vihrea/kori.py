"""Ostoskori, vaihe 7: paljousalennus rivin hinnassa."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Rivi:
    tuote: str
    yksikkohinta: int   # senttejä
    maara: int

    # @alku hinta
    def hinta(self) -> int:
        perus = self.yksikkohinta * self.maara
        if self.maara >= 10:
            # Alennus pyöristetään ylöspäin eli asiakkaan eduksi.
            return perus - (perus * 10 + 99) // 100
        return perus
    # @loppu hinta


class Kori:
    def __init__(self) -> None:
        self._rivit: list[Rivi] = []

    def lisaa(self, tuote: str, hinta: int, maara: int) -> None:
        self._rivit.append(Rivi(tuote, hinta, maara))

    def summa(self) -> int:
        return sum(rivi.hinta() for rivi in self._rivit)

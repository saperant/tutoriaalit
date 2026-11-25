"""Ostoskori, vaihe 5: rivistä tulee oma tyyppinsä."""

from dataclasses import dataclass


# @alku rivi
@dataclass(frozen=True)
class Rivi:
    tuote: str
    yksikkohinta: int   # senttejä
    maara: int

    def hinta(self) -> int:
        return self.yksikkohinta * self.maara


class Kori:
    def __init__(self) -> None:
        self._rivit: list[Rivi] = []

    def lisaa(self, tuote: str, hinta: int, maara: int) -> None:
        self._rivit.append(Rivi(tuote, hinta, maara))

    def summa(self) -> int:
        return sum(rivi.hinta() for rivi in self._rivit)
# @loppu rivi

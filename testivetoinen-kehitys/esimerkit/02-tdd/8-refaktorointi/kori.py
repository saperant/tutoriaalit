"""Ostoskori, vaihe 8: säännöllä on nimi ja vakioilla merkitys."""

from dataclasses import dataclass

PALJOUSRAJA = 10          # kappaletta samaa tuotetta
PALJOUSALENNUS = 10       # prosenttia rivin hinnasta


# @alku saanto
def osuus_ylospain(sentit: int, prosentti: int) -> int:
    """Prosenttiosuus pyöristettynä ylöspäin täyteen senttiin."""
    return (sentit * prosentti + 99) // 100


@dataclass(frozen=True)
class Rivi:
    tuote: str
    yksikkohinta: int   # senttejä
    maara: int

    def perushinta(self) -> int:
        return self.yksikkohinta * self.maara

    def alennus(self) -> int:
        if self.maara < PALJOUSRAJA:
            return 0
        return osuus_ylospain(self.perushinta(), PALJOUSALENNUS)

    def hinta(self) -> int:
        return self.perushinta() - self.alennus()
# @loppu saanto


class Kori:
    def __init__(self) -> None:
        self._rivit: list[Rivi] = []

    def lisaa(self, tuote: str, hinta: int, maara: int) -> None:
        self._rivit.append(Rivi(tuote, hinta, maara))

    def summa(self) -> int:
        return sum(rivi.hinta() for rivi in self._rivit)

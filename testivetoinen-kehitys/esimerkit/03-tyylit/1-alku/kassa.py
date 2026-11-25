"""Kassa: varaa tuotteet varastosta ja veloittaa summan."""

from dataclasses import dataclass
from typing import Protocol


class Varasto(Protocol):
    def varaa(self, tuote: str, maara: int) -> None: ...
    def vapauta(self, tuote: str, maara: int) -> None: ...


class Maksut(Protocol):
    def veloita(self, kortti: str, sentit: int) -> bool: ...


class MaksuEpaonnistui(Exception):
    pass


@dataclass(frozen=True)
class Kuitti:
    summa: int   # senttejä


# @alku kassa
class Kassa:
    def __init__(self, varasto: Varasto, maksut: Maksut,
                 hinnat: dict[str, int]) -> None:
        self._varasto = varasto
        self._maksut = maksut
        self._hinnat = hinnat

    def osta(self, ostokset: dict[str, int], kortti: str) -> Kuitti:
        summa = sum(self._hinnat[t] * m for t, m in ostokset.items())
        for tuote, maara in ostokset.items():
            self._varasto.varaa(tuote, maara)
        if not self._maksut.veloita(kortti, summa):
            for tuote, maara in ostokset.items():
                self._varasto.vapauta(tuote, maara)
            raise MaksuEpaonnistui(kortti)
        return Kuitti(summa)
# @loppu kassa

"""Kassa, refaktoroitu: varasto varaa koko ostoksen yhdellä kutsulla."""

from dataclasses import dataclass
from typing import Protocol


# @alku rajapinta
class Varasto(Protocol):
    def varaa(self, tuote: str, maara: int) -> None: ...
    def vapauta(self, tuote: str, maara: int) -> None: ...
    def varaa_kaikki(self, ostokset: dict[str, int]) -> None: ...
    def vapauta_kaikki(self, ostokset: dict[str, int]) -> None: ...
# @loppu rajapinta


class Maksut(Protocol):
    def veloita(self, kortti: str, sentit: int) -> bool: ...


class MaksuEpaonnistui(Exception):
    pass


@dataclass(frozen=True)
class Kuitti:
    summa: int   # senttejä


class Kassa:
    def __init__(self, varasto: Varasto, maksut: Maksut,
                 hinnat: dict[str, int]) -> None:
        self._varasto = varasto
        self._maksut = maksut
        self._hinnat = hinnat

    # @alku osta
    def osta(self, ostokset: dict[str, int], kortti: str) -> Kuitti:
        summa = sum(self._hinnat[t] * m for t, m in ostokset.items())
        self._varasto.varaa_kaikki(ostokset)
        if not self._maksut.veloita(kortti, summa):
            self._varasto.vapauta_kaikki(ostokset)
            raise MaksuEpaonnistui(kortti)
        return Kuitti(summa)
    # @loppu osta

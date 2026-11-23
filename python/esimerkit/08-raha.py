"""Erikoismetodit: oma arvotyyppi, joka käyttäytyy kuin sisäänrakennettu."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


# @alku raha
@dataclass(frozen=True, slots=True)
class Raha:
    maara: Decimal
    valuutta: str = "EUR"

    def __post_init__(self) -> None:
        pyoristetty = self.maara.quantize(Decimal("0.01"), ROUND_HALF_UP)
        object.__setattr__(self, "maara", pyoristetty)

    def _sama_valuutta(self, toinen: Raha) -> None:
        if toinen.valuutta != self.valuutta:
            raise ValueError(f"{self.valuutta} ja {toinen.valuutta}")

    def __add__(self, toinen: Raha) -> Raha:
        self._sama_valuutta(toinen)
        return Raha(self.maara + toinen.maara, self.valuutta)

    def __mul__(self, kerroin: int | Decimal) -> Raha:
        return Raha(self.maara * kerroin, self.valuutta)

    def __lt__(self, toinen: Raha) -> bool:
        self._sama_valuutta(toinen)
        return self.maara < toinen.maara

    def __str__(self) -> str:
        return f"{self.maara:.2f} {self.valuutta}"
# @loppu raha


# @alku kaytto
hinta = Raha(Decimal("19.90"))
rahti = Raha(Decimal("4.5"))
yhteensa = hinta * 3 + rahti
print(yhteensa, repr(rahti))
print(min([hinta, rahti, yhteensa]))
print(sum([hinta, rahti], start=Raha(Decimal(0))))
alv = yhteensa * Decimal("0.255")
print(alv)                       # pyöristys sentteihin
# @loppu kaytto

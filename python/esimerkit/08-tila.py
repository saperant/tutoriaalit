"""Luettelotyyppi ja kattava match: mypy huomaa puuttuvan tapauksen."""

from enum import Enum, auto
from typing import assert_never


# @alku tila
class Tila(Enum):
    LUONNOS = auto()
    TARKASTETTAVANA = auto()
    JULKAISTU = auto()


def seuraava(tila: Tila) -> Tila:
    match tila:
        case Tila.LUONNOS:
            return Tila.TARKASTETTAVANA
        case Tila.TARKASTETTAVANA:
            return Tila.JULKAISTU
        case Tila.JULKAISTU:
            return Tila.JULKAISTU
        case _:
            assert_never(tila)     # mypy: virhe, jos tapaus puuttuu


tila = Tila.LUONNOS
for _ in range(3):
    print(tila.name, tila.value)
    tila = seuraava(tila)
# @loppu tila

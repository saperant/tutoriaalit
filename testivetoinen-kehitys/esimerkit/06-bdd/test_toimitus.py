"""Askelmäärittelyt: liima määrittelyn lauseiden ja koodin välillä."""

from dataclasses import dataclass

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from toimitus import toimitusmaksu

scenarios("ominaisuudet/toimitus.feature")


def luku(teksti: str, kerroin: int) -> int:
    """'49,99' ja kerroin 100 -> 4999; '1,5' ja kerroin 1000 -> 1500."""
    kokonaiset, _, desimaalit = teksti.partition(",")
    numerot = len(str(kerroin)) - 1
    return int(kokonaiset) * kerroin + int(desimaalit.ljust(numerot, "0"))


# @alku askeleet
@dataclass
class Kassa:
    arvo_snt: int = 0
    paino_g: int = 0
    maksu_snt: int | None = None
    ilmoitus: str | None = None


@pytest.fixture
def kassa() -> Kassa:
    return Kassa()


@given(parsers.parse("että korin arvo on {arvo} euroa"))
def korin_arvo(kassa: Kassa, arvo: str) -> None:
    kassa.arvo_snt = luku(arvo, 100)


@given(parsers.parse("korin paino on {paino} kg"))
def korin_paino(kassa: Kassa, paino: str) -> None:
    kassa.paino_g = luku(paino, 1000)


@when("asiakas siirtyy kassalle")
def siirry_kassalle(kassa: Kassa) -> None:
    try:
        kassa.maksu_snt = toimitusmaksu(kassa.paino_g, kassa.arvo_snt)
    except ValueError as virhe:
        kassa.ilmoitus = str(virhe)


@then(parsers.parse("toimitusmaksu on {maksu} euroa"))
def toimitusmaksu_on(kassa: Kassa, maksu: str) -> None:
    assert kassa.maksu_snt == luku(maksu, 100)


@then(parsers.parse('asiakas näkee ilmoituksen "{teksti}"'))
def ilmoitus_nakyy(kassa: Kassa, teksti: str) -> None:
    assert kassa.ilmoitus == teksti
# @loppu askeleet

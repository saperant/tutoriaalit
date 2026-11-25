"""Sama testisarja ajetaan oikeaa ja viallista toteutusta vasten."""

from collections.abc import Callable

import pytest
import toimitus
import toimitus_viallinen

Maksufunktio = Callable[[int, int], int]


# @alku toteutukset
@pytest.fixture(params=["oikea", "viallinen"])
def toimitusmaksu(request: pytest.FixtureRequest) -> Maksufunktio:
    if request.param == "oikea":
        return toimitus.toimitusmaksu
    return toimitus_viallinen.toimitusmaksu
# @loppu toteutukset

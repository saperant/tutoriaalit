"""Sama testisarja ajetaan oikeaa ja viallista toteutusta vasten."""

from collections.abc import Callable

import pytest
import vahvistus
import vahvistus_viallinen

Vahvistusfunktio = Callable[..., str]


@pytest.fixture(params=["oikea", "viallinen"])
def vahvista(request: pytest.FixtureRequest) -> Vahvistusfunktio:
    if request.param == "oikea":
        return vahvistus.vahvistus
    return vahvistus_viallinen.vahvistus

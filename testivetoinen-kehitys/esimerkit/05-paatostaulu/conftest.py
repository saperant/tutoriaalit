"""Sama testisarja ajetaan oikeaa ja viallista toteutusta vasten."""

from collections.abc import Callable

import alennus
import alennus_viallinen
import pytest

Alennusfunktio = Callable[[bool, bool, bool], int]


@pytest.fixture(params=["oikea", "viallinen"])
def alennusprosentti(request: pytest.FixtureRequest) -> Alennusfunktio:
    if request.param == "oikea":
        return alennus.alennusprosentti
    return alennus_viallinen.alennusprosentti

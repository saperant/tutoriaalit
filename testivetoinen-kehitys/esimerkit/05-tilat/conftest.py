"""Sama testisarja ajetaan oikeaa ja viallista toteutusta vasten."""

from collections.abc import Callable
from typing import Protocol

import pytest
import tilaus
import tilaus_viallinen
from tilaus import Tila


class TilausOlio(Protocol):
    tila: Tila

    def kasittele(self, tapahtuma: str) -> None: ...


TilausLuokka = Callable[..., TilausOlio]


@pytest.fixture(params=["oikea", "viallinen"])
def uusi_tilaus(request: pytest.FixtureRequest) -> TilausLuokka:
    if request.param == "oikea":
        return tilaus.Tilaus
    return tilaus_viallinen.Tilaus

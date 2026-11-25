"""Malliratkaisu 10-2: Testit kellonajan jäsennykselle."""

import pytest

from kellonaika import minuutteina


@pytest.mark.parametrize(("teksti", "odotettu"), [
    ("7:05", 425),       # 7 * 60 + 5
    ("0:00", 0),         # vuorokauden ensimmäinen minuutti
    ("23:59", 1439),     # ja viimeinen
    ("09:30", 570),      # etunolla sallitaan
])
def test_kelvollinen_kellonaika(teksti: str, odotettu: int) -> None:
    assert minuutteina(teksti) == odotettu


@pytest.mark.parametrize("teksti", [
    "24:00",     # tunnit yksi yli
    "7:60",      # minuutit yksi yli
    "7",         # kaksoispiste puuttuu
    "abc",       # ei numeroita
    "",          # tyhjä
])
def test_virheellinen_kellonaika(teksti: str) -> None:
    with pytest.raises(ValueError):
        minuutteina(teksti)

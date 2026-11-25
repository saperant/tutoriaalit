"""Asetusten lukemisen testit."""

import pytest
from viite.asetukset import Asetukset, lue


def test_oletukset() -> None:
    assert lue({}) == Asetukset("kehitys", True)


def test_ymparisto_ja_ryhmittely() -> None:
    muuttujat = {"VIITE_YMPARISTO": "tuotanto", "VIITE_RYHMITTELY": "0"}
    assert lue(muuttujat) == Asetukset("tuotanto", False)


@pytest.mark.parametrize("muuttujat", [
    {"VIITE_YMPARISTO": "prod"},
    {"VIITE_RYHMITTELY": "kyllä"},
])
def test_tuntematon_arvo_hylataan(muuttujat: dict[str, str]) -> None:
    with pytest.raises(ValueError):
        lue(muuttujat)

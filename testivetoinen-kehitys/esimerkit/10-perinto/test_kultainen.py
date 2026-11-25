"""Karakterisointitesti: toteutuksen on tuotettava tallennetut tulosteet."""

import lasku_luonnos
import lasku_uusi
import lasku_vanha
import pytest
from tapaukset import TAPAUKSET, Laskufunktio, tallennetut, tulosta

KULTAINEN = tallennetut()


# @alku testi
@pytest.mark.parametrize(
    "lasku", [lasku_vanha.lasku, lasku_luonnos.lasku, lasku_uusi.lasku],
    ids=["vanha", "luonnos", "uusi"])
@pytest.mark.parametrize(
    ("nimi", "tyyppi", "koodi", "kori"), TAPAUKSET,
    ids=[tapaus[0] for tapaus in TAPAUKSET])
def test_tuloste_vastaa_tallennettua(lasku: Laskufunktio, nimi: str,
                                     tyyppi: int, koodi: str,
                                     kori: str) -> None:
    assert tulosta(lasku, tyyppi, koodi, kori) == KULTAINEN[nimi]


def test_aineisto_kattaa_kaikki_tapaukset() -> None:
    assert set(KULTAINEN) == {tapaus[0] for tapaus in TAPAUKSET}
# @loppu testi

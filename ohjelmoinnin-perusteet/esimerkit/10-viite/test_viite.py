"""Viitenumeron testit. Aja hakemistossa komennolla: pytest -q"""

import pytest

from viite import laske_tarkiste, muodosta_viite, on_kelvollinen


def test_tunnettu_viite() -> None:
    assert muodosta_viite("123456") == "1234561"


def test_tarkiste_nolla_kun_summa_tasakymmenia() -> None:
    # 1*7 + 0*3 + 3*1 = 10, joten tarkiste on 0 eikä 10.
    assert laske_tarkiste("301") == 0


@pytest.mark.parametrize("viite", ["1234561", "12345 61", "1009"])
def test_kelvolliset(viite: str) -> None:
    assert on_kelvollinen(viite)


@pytest.mark.parametrize("viite", [
    "1234562",       # väärä tarkiste
    "123",           # liian lyhyt
    "12a4561",       # kirjain
    "",              # tyhjä
    "1" * 21,        # liian pitkä
])
def test_virheelliset(viite: str) -> None:
    assert not on_kelvollinen(viite)


@pytest.mark.parametrize("perusosa", ["12", "12x", "1" * 20])
def test_virheellinen_perusosa(perusosa: str) -> None:
    with pytest.raises(ValueError):
        laske_tarkiste(perusosa)

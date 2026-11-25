"""Jokainen ehto testataan yksinään: yhdistelmät jäävät kokeilematta."""

from conftest import Alennusfunktio


# @alku erikseen
def test_ei_alennusta(alennusprosentti: Alennusfunktio) -> None:
    assert alennusprosentti(False, False, False) == 0


def test_kanta_asiakas(alennusprosentti: Alennusfunktio) -> None:
    assert alennusprosentti(True, False, False) == 5


def test_kampanjakoodi(alennusprosentti: Alennusfunktio) -> None:
    assert alennusprosentti(False, True, False) == 10


def test_iso_tilaus(alennusprosentti: Alennusfunktio) -> None:
    assert alennusprosentti(False, False, True) == 5


def test_kanta_asiakkaan_iso_tilaus(alennusprosentti: Alennusfunktio) -> None:
    assert alennusprosentti(True, False, True) == 10
# @loppu erikseen

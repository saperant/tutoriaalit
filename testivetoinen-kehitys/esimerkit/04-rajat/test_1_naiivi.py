"""Testit, jotka syntyvät kokeilemalla "tavallisia" arvoja."""

import pytest
from conftest import Maksufunktio


# @alku naiivi
def test_kevyt_paketti(toimitusmaksu: Maksufunktio) -> None:
    assert toimitusmaksu(500, 2_000) == 590


def test_keskikokoinen_paketti(toimitusmaksu: Maksufunktio) -> None:
    assert toimitusmaksu(5_000, 2_000) == 990


def test_raskas_paketti(toimitusmaksu: Maksufunktio) -> None:
    assert toimitusmaksu(20_000, 2_000) == 1_990


def test_iso_tilaus_on_ilmainen(toimitusmaksu: Maksufunktio) -> None:
    assert toimitusmaksu(1_000, 8_000) == 0


def test_negatiivinen_paino_hylataan(toimitusmaksu: Maksufunktio) -> None:
    with pytest.raises(ValueError, match="positiivinen"):
        toimitusmaksu(-5, 2_000)
# @loppu naiivi

"""Testit, jotka suorittavat joka rivin ja haaran mutta väittävät vähän."""

import pytest
from toimitus import toimitusmaksu, veloitettava


# @alku heikko
def test_kelvoton_paino() -> None:
    with pytest.raises(ValueError):
        toimitusmaksu(-5, 2_000)
    with pytest.raises(ValueError):
        toimitusmaksu(50_000, 2_000)


def test_maksuluokat() -> None:
    assert toimitusmaksu(1_000, 2_000) == 590
    assert toimitusmaksu(5_000, 2_000) == 990
    assert toimitusmaksu(20_000, 2_000) == 1_990


def test_iso_tilaus_on_ilmainen() -> None:
    assert toimitusmaksu(1_000, 8_000) == 0


def test_hyvitys() -> None:
    assert veloitettava(590, 1_000) == 0
    assert veloitettava(990, 500) > 0
# @loppu heikko

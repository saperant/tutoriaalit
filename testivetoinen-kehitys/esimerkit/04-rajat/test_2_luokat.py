"""Yksi edustaja jokaisesta ekvivalenssiluokasta."""

import pytest
from conftest import Maksufunktio


# @alku luokat
@pytest.mark.parametrize(
    ("paino", "summa", "maksu"),
    [
        pytest.param(1_000, 2_000, 590, id="pieni-paketti"),
        pytest.param(6_000, 2_000, 990, id="iso-paketti"),
        pytest.param(20_000, 2_000, 1_990, id="rahti"),
        pytest.param(1_000, 8_000, 0, id="pieni-ilmainen"),
        pytest.param(6_000, 8_000, 0, id="iso-ilmainen"),
        pytest.param(20_000, 8_000, 1_990, id="rahti-ei-ilmainen"),
    ],
)
def test_kelvolliset_luokat(toimitusmaksu: Maksufunktio, paino: int,
                            summa: int, maksu: int) -> None:
    assert toimitusmaksu(paino, summa) == maksu


@pytest.mark.parametrize("paino", [-100, 45_000], ids=["neg", "liikaa"])
def test_kelvottomat_luokat(toimitusmaksu: Maksufunktio,
                            paino: int) -> None:
    with pytest.raises(ValueError):
        toimitusmaksu(paino, 2_000)
# @loppu luokat

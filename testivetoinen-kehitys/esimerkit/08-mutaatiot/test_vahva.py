"""Samat tapaukset ja lisäksi rajat ja täsmälliset väitteet."""

import pytest
from toimitus import toimitusmaksu, veloitettava


@pytest.mark.parametrize("paino", [-5, 0, 30_001, 50_000])
def test_kelvoton_paino(paino: int) -> None:
    with pytest.raises(ValueError):
        toimitusmaksu(paino, 2_000)


# @alku vahva
@pytest.mark.parametrize(
    ("paino", "maksu"),
    [(1, 590), (2_000, 590), (2_001, 990), (10_000, 990),
     (10_001, 1_990), (30_000, 1_990)],
)
def test_painorajat(paino: int, maksu: int) -> None:
    assert toimitusmaksu(paino, 2_000) == maksu


@pytest.mark.parametrize(
    ("paino", "summa", "maksu"),
    [(1_000, 4_999, 590), (1_000, 5_000, 0), (10_000, 5_000, 0),
     (10_001, 5_000, 1_990)],
)
def test_ilmaisen_toimituksen_rajat(paino: int, summa: int,
                                    maksu: int) -> None:
    assert toimitusmaksu(paino, summa) == maksu


@pytest.mark.parametrize(
    ("maksu", "hyvitys", "jaa"),
    [(590, 1_000, 0), (590, 590, 0), (990, 500, 490), (990, 0, 990)],
)
def test_hyvitys(maksu: int, hyvitys: int, jaa: int) -> None:
    assert veloitettava(maksu, hyvitys) == jaa
# @loppu vahva

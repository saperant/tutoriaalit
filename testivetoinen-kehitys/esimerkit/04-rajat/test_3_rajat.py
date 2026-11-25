"""Raja-arvoanalyysi: jokaisen rajan molemmat puolet."""

import pytest
from conftest import Maksufunktio


# @alku rajat
@pytest.mark.parametrize(
    ("paino", "maksu"),
    [(1, 590), (2_000, 590), (2_001, 990), (10_000, 990),
     (10_001, 1_990), (30_000, 1_990)],
)
def test_painorajat(toimitusmaksu: Maksufunktio, paino: int,
                    maksu: int) -> None:
    assert toimitusmaksu(paino, 2_000) == maksu


@pytest.mark.parametrize(("summa", "maksu"), [(4_999, 590), (5_000, 0)])
def test_ilmaisen_toimituksen_raja(toimitusmaksu: Maksufunktio,
                                   summa: int, maksu: int) -> None:
    assert toimitusmaksu(1_000, summa) == maksu


@pytest.mark.parametrize("paino", [0, 30_001])
def test_kelvottoman_painon_rajat(toimitusmaksu: Maksufunktio,
                                  paino: int) -> None:
    with pytest.raises(ValueError):
        toimitusmaksu(paino, 2_000)
# @loppu rajat

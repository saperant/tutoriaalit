"""Päätöstaulun jokainen sarake on yksi testitapaus."""

import pytest
from conftest import Alennusfunktio

K, E = True, False

# @alku taulu
#   kanta-asiakas, kampanjakoodi, iso tilaus -> alennusprosentti
PAATOSTAULU = [
    (E, E, E, 0),
    (E, E, K, 5),
    (E, K, E, 10),
    (E, K, K, 10),
    (K, E, E, 5),
    (K, E, K, 10),
    (K, K, E, 10),
    (K, K, K, 15),
]


def tunniste(saanto: tuple[bool, bool, bool, int]) -> str:
    return "".join("K" if ehto else "E" for ehto in saanto[:3])


@pytest.mark.parametrize("saanto", PAATOSTAULU, ids=tunniste)
def test_paatostaulu(alennusprosentti: Alennusfunktio,
                     saanto: tuple[bool, bool, bool, int]) -> None:
    kanta, koodi, iso, odotettu = saanto

    assert alennusprosentti(kanta, koodi, iso) == odotettu


def test_taulu_kattaa_kaikki_yhdistelmat() -> None:
    assert len({saanto[:3] for saanto in PAATOSTAULU}) == 2 ** 3
# @loppu taulu

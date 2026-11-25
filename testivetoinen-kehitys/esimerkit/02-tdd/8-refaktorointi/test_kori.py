"""Ostoskorin testit, vaihe 8: myös testit refaktoroidaan."""

import pytest
from kori import Kori


def test_tyhjan_korin_summa_on_nolla() -> None:
    kori = Kori()

    assert kori.summa() == 0


def test_summa_on_rivien_hinta_kertaa_maara() -> None:
    kori = Kori()
    kori.lisaa("kahvi", hinta=549, maara=2)
    kori.lisaa("suodatinpussit", hinta=189, maara=1)

    assert kori.summa() == 2 * 549 + 189


# @alku taulukko
@pytest.mark.parametrize(
    ("hinta", "maara", "summa"),
    [
        pytest.param(500, 9, 4500, id="raja-alla-ei-alennusta"),
        pytest.param(500, 10, 4500, id="rajalla-kymmenen-prosenttia"),
        pytest.param(333, 11, 3296, id="pyoristys-asiakkaan-eduksi"),
    ],
)
def test_paljousalennus(hinta: int, maara: int, summa: int) -> None:
    kori = Kori()
    kori.lisaa("tuote", hinta=hinta, maara=maara)

    assert kori.summa() == summa
# @loppu taulukko

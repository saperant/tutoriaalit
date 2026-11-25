"""Tyypilliset polut: onnistunut tilaus ja peruutus."""

from conftest import TilausLuokka
from tilaus import Tila


# @alku polut
def test_tilaus_etenee_toimitukseen(uusi_tilaus: TilausLuokka) -> None:
    tilaus = uusi_tilaus()

    for tapahtuma in ("maksa", "laheta", "toimita"):
        tilaus.kasittele(tapahtuma)

    assert tilaus.tila is Tila.TOIMITETTU


def test_maksetun_tilauksen_voi_perua(uusi_tilaus: TilausLuokka) -> None:
    tilaus = uusi_tilaus()
    tilaus.kasittele("maksa")

    tilaus.kasittele("peru")

    assert tilaus.tila is Tila.PERUTTU
# @loppu polut

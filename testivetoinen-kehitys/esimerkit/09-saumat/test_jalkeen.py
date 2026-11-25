"""Ytimen testit: syöte sisään, arvo ulos, ei paikkauksia."""

import random
from datetime import date, datetime

import pytest
from jalkeen import lahtopaiva, saapumispaiva, seurantakoodi, vahvista


# @alku ydintestit
@pytest.mark.parametrize(
    ("tilattu", "lahto"),
    [
        pytest.param(datetime(2026, 11, 25, 14, 59), date(2026, 11, 25),
                     id="ke-ennen-kolmea-samana-paivana"),
        pytest.param(datetime(2026, 11, 25, 15, 0), date(2026, 11, 26),
                     id="ke-kolmelta-seuraavana-paivana"),
        pytest.param(datetime(2026, 11, 27, 16, 30), date(2026, 11, 30),
                     id="pe-ilta-maanantaina"),
        pytest.param(datetime(2026, 11, 28, 9, 0), date(2026, 11, 30),
                     id="la-maanantaina"),
    ],
)
def test_lahtopaiva(tilattu: datetime, lahto: date) -> None:
    assert lahtopaiva(tilattu) == lahto


@pytest.mark.parametrize(
    ("lahto", "saapuu"),
    [
        pytest.param(date(2026, 11, 23), date(2026, 11, 25), id="ma-ke"),
        pytest.param(date(2026, 11, 26), date(2026, 11, 30), id="to-ma"),
        pytest.param(date(2026, 11, 27), date(2026, 11, 30), id="pe-ma"),
    ],
)
def test_saapumispaiva(lahto: date, saapuu: date) -> None:
    assert saapumispaiva(lahto) == saapuu


def test_seurantakoodi_on_kuusi_sallittua_merkkia() -> None:
    koodi = seurantakoodi(random.Random(1))

    assert len(koodi) == 6
    assert set(koodi) <= set("ABCDEFGHJKLMNPQRSTUVWXYZ23456789")


def test_vahvistuksen_teksti() -> None:
    vahvistus = vahvista(42, datetime(2026, 11, 27, 16, 30),
                         random.Random(1))

    assert vahvistus.teksti().startswith(
        "Tilaus 42 lähtee 30.11. ja saapuu 02.12. Seurantakoodi: ")
# @loppu ydintestit

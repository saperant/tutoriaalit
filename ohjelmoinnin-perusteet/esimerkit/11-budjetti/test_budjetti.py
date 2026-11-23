"""Budjettiohjelman testit: jäsennys, koosteet ja virheelliset rivit."""

from datetime import date

import pytest

from main import lue_tapahtumat
from raportti import kuukausittain, suurimmat_menot
from tapahtuma import Tapahtuma, jasenna_rivi, jasenna_summa


@pytest.mark.parametrize(("teksti", "sentit"), [
    ("2450,00", 245000), ("-62,40", -6240), ("0,05", 5)])
def test_summa(teksti: str, sentit: int) -> None:
    assert jasenna_summa(teksti) == sentit


@pytest.mark.parametrize("teksti", ["12", "12,5", "1.000,00", "-", ""])
def test_virheellinen_summa(teksti: str) -> None:
    with pytest.raises(ValueError):
        jasenna_summa(teksti)


def test_rivi() -> None:
    assert jasenna_rivi("2026-01-05;Ruoka;-62,40\n") == Tapahtuma(
        date(2026, 1, 5), "ruoka", -6240)


def test_koosteet() -> None:
    tapahtumat = [jasenna_rivi(r) for r in [
        "2026-01-03;palkka;100,00", "2026-01-09;ruoka;-20,00",
        "2026-02-01;ruoka;-5,00", "2026-02-02;kirjat;-30,00"]]
    assert kuukausittain(tapahtumat) == {
        "2026-01": [10000, -2000], "2026-02": [0, -3500]}
    assert suurimmat_menot(tapahtumat, 1) == [("kirjat", 3000)]


def test_virheelliset_rivit_raportoidaan() -> None:
    tapahtumat, virheet = lue_tapahtumat(
        ["# kommentti", "2026-13-01;ruoka;-1,00", "2026-01-01;ruoka"])
    assert tapahtumat == []
    assert len(virheet) == 2 and virheet[1].startswith("rivi 3:")

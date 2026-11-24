"""Rekisterikuvauksen tarkistimen testit."""

from __future__ import annotations

from pathlib import Path

from vuo.rekisterit import Kentta, Lohko, Rekisteri, lue, tarkista

ASETUKSET = Path(__file__).resolve().parent.parent / "asetukset"


def lohko(*kentat: Kentta, osoite: int = 0) -> Lohko:
    return Lohko("t", 0, 32, (Rekisteri("R", osoite, "", kentat),))


def test_kuvaus_kelpaa() -> None:
    assert tarkista(lue(ASETUKSET / "rekisterit.toml")) == []


def test_rikkinainen_kuvaus() -> None:
    assert len(tarkista(lue(ASETUKSET / "rekisterit_rikki.toml"))) == 8


def test_paallekkaiset_kentat() -> None:
    a = Kentta("A", 3, 0, "rw", 0, "")
    b = Kentta("B", 4, 3, "rw", 0, "")
    assert tarkista(lohko(a, b)) == ["R.B: menee päällekkäin toisen "
                                     "kentän kanssa"]


def test_maski() -> None:
    assert Kentta("A", 15, 8, "rw", 0, "").maski == 0xFF00

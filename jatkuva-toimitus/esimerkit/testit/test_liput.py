"""Lippujen ominaisuudet: pysyvyys, tasaisuus ja hätäkatkaisu."""

from dataclasses import replace
from datetime import date

from toimitus.liput import Lippu, lokero, paalla, poistettavat

LIPPU = Lippu("koe", "tiimi", date(2026, 1, 1))
KAYTTAJAT = [f"k{nro}" for nro in range(5000)]


def test_lokero_on_pysyva_ja_valilla() -> None:
    assert lokero("koe", "k1") == lokero("koe", "k1")
    assert all(0 <= lokero("koe", k) < 100 for k in KAYTTAJAT)


def test_osuus_toteutuu_likimain() -> None:
    for osuus in (10, 50, 90):
        paalla_maara = sum(paalla(replace(LIPPU, osuus=osuus), k)
                           for k in KAYTTAJAT)
        assert abs(paalla_maara / len(KAYTTAJAT) - osuus / 100) < 0.03


def test_osuuden_kasvu_ei_pudota_ketaan() -> None:
    pieni = {k for k in KAYTTAJAT if paalla(replace(LIPPU, osuus=20), k)}
    suuri = {k for k in KAYTTAJAT if paalla(replace(LIPPU, osuus=60), k)}
    assert pieni <= suuri


def test_hatakatkaisu_voittaa_kaiken() -> None:
    lippu = replace(LIPPU, osuus=100, sallitut=frozenset({"k1"}),
                    hatakatkaisu=True)
    assert not paalla(lippu, "k1")


def test_poistettavat() -> None:
    vanha = replace(LIPPU, osuus=100)
    kesken = replace(LIPPU, osuus=40)
    pysyva = replace(LIPPU, osuus=100, pysyva=True)
    tuore = Lippu("uusi", "tiimi", date(2026, 5, 30), osuus=100)
    assert poistettavat([vanha, kesken, pysyva, tuore],
                        date(2026, 6, 1)) == [vanha]

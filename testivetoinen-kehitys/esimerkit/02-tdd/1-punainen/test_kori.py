"""Ostoskorin testit, vaihe 1: ensimmäinen testi ennen koodia."""

from kori import Kori


def test_tyhjan_korin_summa_on_nolla() -> None:
    kori = Kori()

    assert kori.summa() == 0

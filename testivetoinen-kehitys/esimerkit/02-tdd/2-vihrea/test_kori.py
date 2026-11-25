"""Ostoskorin testit, vaihe 2: sama testi, nyt vihreä."""

from kori import Kori


def test_tyhjan_korin_summa_on_nolla() -> None:
    kori = Kori()

    assert kori.summa() == 0

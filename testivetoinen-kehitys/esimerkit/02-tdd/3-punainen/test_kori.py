"""Ostoskorin testit, vaihe 3: toinen testi pakottaa yleistämään."""

from kori import Kori


def test_tyhjan_korin_summa_on_nolla() -> None:
    kori = Kori()

    assert kori.summa() == 0


# @alku uusi
def test_summa_on_rivien_hinta_kertaa_maara() -> None:
    kori = Kori()
    kori.lisaa("kahvi", hinta=549, maara=2)
    kori.lisaa("suodatinpussit", hinta=189, maara=1)

    assert kori.summa() == 2 * 549 + 189
# @loppu uusi

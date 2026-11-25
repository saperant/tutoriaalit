"""Ostoskorin testit, vaihe 7: alennustestit vihreinä."""

from kori import Kori


def test_tyhjan_korin_summa_on_nolla() -> None:
    kori = Kori()

    assert kori.summa() == 0


def test_summa_on_rivien_hinta_kertaa_maara() -> None:
    kori = Kori()
    kori.lisaa("kahvi", hinta=549, maara=2)
    kori.lisaa("suodatinpussit", hinta=189, maara=1)

    assert kori.summa() == 2 * 549 + 189


# @alku alennus
def test_kymmenesta_kappaleesta_saa_alennuksen() -> None:
    kori = Kori()
    kori.lisaa("kahvi", hinta=500, maara=10)

    assert kori.summa() == 4500


def test_yhdeksan_kappaletta_ei_saa_alennusta() -> None:
    kori = Kori()
    kori.lisaa("kahvi", hinta=500, maara=9)

    assert kori.summa() == 9 * 500


def test_alennus_pyoristetaan_asiakkaan_eduksi() -> None:
    kori = Kori()
    kori.lisaa("tee", hinta=333, maara=11)   # 3663 snt, 10 % = 366,3 snt

    assert kori.summa() == 3663 - 367
# @loppu alennus

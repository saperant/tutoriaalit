"""Testejä, jotka menevät läpi mutta ovat raskaita ylläpitää."""

from kori import Kori

kori = Kori()   # yhteinen kori: testit riippuvat toistensa järjestyksestä


# @alku haju
def test_1() -> None:
    kori.lisaa("kahvi", 549, 2)
    assert kori.summa() == 1098
    assert len(kori._rivit) == 1
    kori.lisaa("tee", 333, 11)
    odotettu = 1098
    for rivi in kori._rivit[1:]:
        hinta = rivi.yksikkohinta * rivi.maara
        if rivi.maara >= 10:
            hinta -= (hinta * 10 + 99) // 100
        odotettu += hinta
    assert kori.summa() == odotettu


def test_2() -> None:
    assert kori.summa() == 4394     # toimii vain test_1:n jälkeen
# @loppu haju

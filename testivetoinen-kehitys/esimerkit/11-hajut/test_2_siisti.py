"""Samat asiat testattuna niin, että testi kertoo, mitä se väittää."""

from kori import Kori


# @alku siisti
def kori_jossa(*rivit: tuple[str, int, int]) -> Kori:
    """Rakentaa korin riveistä (tuote, hinta sentteinä, määrä)."""
    kori = Kori()
    for tuote, hinta, maara in rivit:
        kori.lisaa(tuote, hinta=hinta, maara=maara)
    return kori


def test_summa_on_rivien_hintojen_summa() -> None:
    kori = kori_jossa(("kahvi", 549, 2), ("suodatinpussit", 189, 1))

    assert kori.summa() == 1098 + 189


def test_paljousalennus_koskee_vain_omaa_riviaan() -> None:
    kori = kori_jossa(("kahvi", 549, 2), ("tee", 333, 11))

    assert kori.summa() == 1098 + 3296    # tee: 3663 - 367
# @loppu siisti

"""Esimerkkipohjaiset testit: kirjoittajan keksimät arvot."""

from raha import jaa_tasan, jasenna, muotoile, prosentti


# @alku esimerkit
def test_muotoilu() -> None:
    assert muotoile(1234) == "12,34"
    assert muotoile(99) == "0,99"


def test_jasennys() -> None:
    assert jasenna("12,34") == 1234
    assert jasenna("7,5") == 750


def test_jako() -> None:
    assert jaa_tasan(900, 3) == [300, 300, 300]


def test_prosentti() -> None:
    assert prosentti(1000, 24) == 240
    assert prosentti(999, 10) == 100
# @loppu esimerkit

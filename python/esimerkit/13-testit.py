"""pytest-testit ja niiden ajo ohjelmasta käsin.

Tavallisesti testit ovat tiedostoissa tests/test_*.py ja ne ajetaan
komennolla `pytest`. Tämä esimerkki ajaa itsensä, jotta tuloste
voidaan tarkistaa.
"""

import sys
from decimal import Decimal
from pathlib import Path

import pytest


# @alku koodi
def jasenna_summa(teksti: str) -> Decimal:
    """Jäsentää summan muodossa '12,50' tai '12.50 €'.

    >>> jasenna_summa("12,50 €")
    Decimal('12.50')
    """
    puhdas = teksti.strip().removesuffix("€").strip().replace(",", ".")
    try:
        summa = Decimal(puhdas)
    except ArithmeticError:
        raise ValueError(f"virheellinen summa: {teksti!r}") from None
    if summa < 0:
        raise ValueError(f"negatiivinen summa: {teksti!r}")
    return summa
# @loppu koodi


# @alku testit
@pytest.mark.parametrize(("syote", "odotettu"), [
    ("12,50", Decimal("12.50")),
    (" 7.5 € ", Decimal("7.5")),
    ("0", Decimal("0")),
], ids=["pilkku", "euromerkki", "nolla"])
def test_kelvolliset(syote: str, odotettu: Decimal) -> None:
    assert jasenna_summa(syote) == odotettu


@pytest.mark.parametrize("syote", ["", "abc", "-1"],
                         ids=["tyhja", "kirjaimet", "negatiivinen"])
def test_virheelliset(syote: str) -> None:
    with pytest.raises(ValueError, match="summa"):
        jasenna_summa(syote)


@pytest.fixture
def kulutiedosto(tmp_path: Path) -> Path:
    polku = tmp_path / "kulut.txt"
    polku.write_text("12,50\n7.5 €\n", encoding="utf-8")
    return polku


def test_tiedostosta(kulutiedosto: Path) -> None:
    rivit = kulutiedosto.read_text(encoding="utf-8").splitlines()
    assert sum(map(jasenna_summa, rivit)) == Decimal("20.00")
# @loppu testit


class Raportti:
    """pytest-liitännäinen, joka kerää testien tulokset."""

    def __init__(self) -> None:
        self.tulokset: list[tuple[str, str]] = []

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        if report.when == "call" or report.outcome != "passed":
            self.tulokset.append((report.nodeid.split("::")[-1],
                                  report.outcome))


if __name__ == "__main__":
    raportti = Raportti()
    koodi = pytest.main([__file__, "--doctest-modules", "-p", "no:terminal",
                         "-p", "no:cacheprovider"], plugins=[raportti])
    for nimi, tulos in raportti.tulokset:
        print(f"{tulos:<7} {nimi}")
    print("paluuarvo:", int(koodi))
    sys.exit(int(koodi))

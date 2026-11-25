"""Kestojen jäsennyksen ja muotoilun testit."""

import pytest

from kesto import jasenna, muotoile


@pytest.mark.parametrize(("teksti", "sekunnit"), [
    ("45s", 45),
    ("1h30m", 5400),
    ("2d", 172800),
    ("1d1h1m1s", 90061),
])
def test_jasennys_ja_muotoilu_ovat_kaanteisia(teksti: str,
                                              sekunnit: int) -> None:
    assert jasenna(teksti) == sekunnit
    assert muotoile(sekunnit) == teksti


@pytest.mark.parametrize("teksti", ["", "90", "1x", "30m1h", "1h1h", "-5s"])
def test_virheellinen_kesto_hylataan(teksti: str) -> None:
    with pytest.raises(ValueError, match=r"kesto|järjestyksessä"):
        jasenna(teksti)


def test_muotoilu_normalisoi() -> None:
    assert muotoile(jasenna("90m")) == "1h30m"
    assert muotoile(0) == "0s"

"""Jokainen arvo esiintyy ainakin kerran, mutta parit jäävät sattumaan."""

import pytest
from conftest import Vahvistusfunktio


# @alku arvot
@pytest.mark.parametrize(
    ("maksutapa", "toimitus", "asiakas", "kieli"),
    [
        ("kortti", "nouto", "yksityinen", "fi"),
        ("lasku", "posti", "yritys", "sv"),
        ("mobiili", "automaatti", "yksityinen", "en"),
    ],
)
def test_jokainen_arvo_kerran(vahvista: Vahvistusfunktio, maksutapa: str,
                              toimitus: str, asiakas: str,
                              kieli: str) -> None:
    assert vahvista(maksutapa, toimitus, asiakas, kieli)
# @loppu arvot

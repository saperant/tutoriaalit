"""Analyyttisten mallien testit: rajatapaukset ja tunnetut arvot."""

import math

from arkki.mallit import (Taso, amdahl, dynaaminen, epasymmetrinen,
                          gustafson, littlen_kaista, roofline, symmetrinen)


def test_amdahl_rajat() -> None:
    assert amdahl(0.0, 10) == 1.0
    assert math.isclose(amdahl(1.0, 10), 10.0)
    assert math.isclose(amdahl(0.5, 1e12), 2.0, rel_tol=1e-9)


def test_gustafson() -> None:
    assert gustafson(0.9, 10) == 9.1


# @alku hill-marty
def test_hill_marty_pienilla_ytimilla_on_amdahl() -> None:
    # r = 1: kaikki rakenteet ovat n pientä ydintä, eli Amdahlin laki.
    for malli in (symmetrinen, epasymmetrinen, dynaaminen):
        assert math.isclose(malli(0.9, 64, 1), amdahl(0.9, 64))


def test_dynaaminen_on_aina_paras() -> None:
    for r in (2, 4, 8, 16):
        assert dynaaminen(0.95, 64, r) >= epasymmetrinen(0.95, 64, r)
        assert epasymmetrinen(0.95, 64, r) >= symmetrinen(0.95, 64, r)
# @loppu hill-marty


def test_roofline_valitsee_matalimman_katon() -> None:
    tasot = [Taso("L1", 100.0, 1.0), Taso("muisti", 10.0, 0.5)]
    assert roofline(50.0, tasot) == (5.0, "muisti")
    assert roofline(1.0, tasot) == (1.0, "laskenta")


def test_littlen_laki() -> None:
    assert littlen_kaista(10, 64, 64.0) == 10.0

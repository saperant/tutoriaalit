"""Mittarien laskenta pienellä käsin tarkistettavalla historialla."""

from datetime import datetime, timedelta

from toimitus.dora import Julkaisu, laske

ALKU = datetime(2026, 3, 2, 12, 0)


def test_nelja_mittaria() -> None:
    julkaisut = [
        Julkaisu(ALKU, (ALKU - timedelta(hours=2),
                        ALKU - timedelta(hours=6))),
        Julkaisu(ALKU + timedelta(days=7),
                 (ALKU + timedelta(days=6),),
                 korjattu=ALKU + timedelta(days=7, hours=3)),
    ]
    mittarit = laske(julkaisut, viikkoja=2)
    assert mittarit.tiheys == 1.0
    assert mittarit.lapimeno == 6.0          # mediaani luvuista 2, 6, 24
    assert mittarit.epaonnistui == 0.5
    assert mittarit.palautuminen == 3.0


def test_ilman_vikoja_palautumisaika_on_nolla() -> None:
    julkaisut = [Julkaisu(ALKU, (ALKU - timedelta(hours=1),))]
    assert laske(julkaisut, viikkoja=1).palautuminen == 0.0

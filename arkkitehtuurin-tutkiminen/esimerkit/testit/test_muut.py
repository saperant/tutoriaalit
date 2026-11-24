"""Intervallimallin, tutkimusfunktioiden ja tehomallin testit."""

import math
import random

from arkki.intervalli import Ydin, intervallimalli, kmeans
from arkki.teho import Piiri
from arkki.tutkimus import herkkyys, latinalainen, pareto, ruudukko


def test_intervallimalli_limitys() -> None:
    ydin = Ydin(ikkuna=10, perus_cpi=0.25, huti=100, haara=10)
    assert intervallimalli("aaaa", ydin) == 1.0
    # Toinen huti on ikkunan sisällä: piiloutuu. Kolmas ei ole.
    kaskyt = "m" + "a" * 4 + "m" + "a" * 20 + "m"
    assert intervallimalli(kaskyt, ydin) == len(kaskyt) * 0.25 + 200
    assert intervallimalli("mdd", ydin) == 0.75 + 300  # riippuvat


def test_kmeans_erottaa_ryhmat() -> None:
    pisteet = [[0.0, 0.0], [0.1, 0.0], [5.0, 5.0], [5.1, 5.0]]
    r = kmeans(pisteet, 2, siemen=1)
    assert r[0] == r[1] and r[2] == r[3] and r[0] != r[2]


# @alku hyperkuutio
def test_hyperkuutio_kayttaa_jokaista_tasoa_kerran() -> None:
    tila = {"a": [1, 2, 3, 4], "b": [10, 20, 30, 40]}
    otos = latinalainen(tila, 4, random.Random(1))
    for nimi in tila:
        assert sorted(p[nimi] for p in otos) == tila[nimi]
# @loppu hyperkuutio


def test_ruudukko_ja_pareto() -> None:
    assert len(ruudukko({"a": [1, 2], "b": [1, 2, 3]})) == 6
    assert pareto([(1, 3), (2, 2), (3, 1), (3, 3)]) == [0, 1, 2]


def test_herkkyys_potenssifunktiolle() -> None:
    joustot = herkkyys(lambda p: p["x"] ** 2 * p["y"], {"x": 3.0, "y": 2.0})
    assert math.isclose(joustot["x"], 2.0, rel_tol=0.01)
    assert math.isclose(joustot["y"], 1.0)


def test_piiri_nimellispisteessa() -> None:
    p = Piiri(kapasitanssi_nf=10.0)
    assert math.isclose(p.taajuus(1.0), 3.0)
    assert math.isclose(p.dynaaminen(0.5, 1.0) * 4, p.dynaaminen(1.0, 1.0))
    assert math.isclose(p.vuoto(1.0), 2.0)

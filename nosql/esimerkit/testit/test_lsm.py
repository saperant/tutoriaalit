"""LSM-puu käyttäytyy kuten sanakirja satunnaisilla operaatioilla."""

import random
from pathlib import Path

from nosql.lsm import LSM, Bloom


def test_lsm_vastaa_mallia(tmp_path: Path) -> None:
    satunnainen = random.Random(2026)
    puu = LSM(tmp_path, memtable_koko=8)
    malli: dict[str, str] = {}
    for kierros in range(2000):
        avain = f"k{satunnainen.randrange(100)}"
        if satunnainen.random() < 0.2:
            puu.poista(avain)
            malli.pop(avain, None)
        else:
            arvo = f"v{kierros}"
            puu.aseta(avain, arvo)
            malli[avain] = arvo
        if kierros % 500 == 499:
            puu.kompaktoi()
        tarkistettava = f"k{satunnainen.randrange(100)}"
        assert puu.hae(tarkistettava) == malli.get(tarkistettava)


def test_bloom_ei_valehtele_puuttumisesta() -> None:
    bloom = Bloom(bitteja=1000, tiivisteita=7)
    for i in range(100):
        bloom.lisaa(f"a{i}")
    assert all(bloom.ehka(f"a{i}") for i in range(100))
    vaarat = sum(bloom.ehka(f"b{i}") for i in range(10_000))
    assert vaarat < 200        # teoriassa noin 0,8 %

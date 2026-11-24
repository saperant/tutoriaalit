"""Yhteisen koodin yksikkötestit: protokolla, hajautus, rajoitin,
histogrammi ja lyhytosoitteen koodi."""

import io
import math
import random

import pytest

from jarjestelma.hajautus import Rendezvous, Rengas
from jarjestelma.histogrammi import Histogrammi
from jarjestelma.rajoitin import Sanko
from jarjestelma.resp import RedisVirhe, koodaa, lue
from jarjestelma.tunnus import koodi, numero


def test_resp_koodaus() -> None:
    assert koodaa("SET", "k", 5) == \
        b"*3\r\n$3\r\nSET\r\n$1\r\nk\r\n$1\r\n5\r\n"


def test_resp_vastaukset() -> None:
    virta = io.BytesIO(b"+OK\r\n:42\r\n$-1\r\n*2\r\n$1\r\na\r\n:1\r\n")
    assert [lue(virta) for _ in range(4)] == ["OK", 42, None, [b"a", 1]]
    with pytest.raises(RedisVirhe, match="WRONGTYPE"):
        lue(io.BytesIO(b"-WRONGTYPE vaara tyyppi\r\n"))
    with pytest.raises(ConnectionError):
        lue(io.BytesIO(b"+katkesi"))


@pytest.mark.parametrize("tee", [lambda s: Rengas(s, 50), Rendezvous])
def test_poisto_siirtaa_vain_poistetun_avaimet(tee: object) -> None:
    solmut = ["a", "b", "c", "d"]
    ennen = tee(solmut)  # type: ignore[operator]
    jalkeen = tee(["a", "b", "d"])  # type: ignore[operator]
    for i in range(2000):
        avain = f"k{i}"
        if ennen.solmu(avain) != "c":
            assert jalkeen.solmu(avain) == ennen.solmu(avain)


def test_rengas_lisays_ja_poisto_palauttavat_jaon() -> None:
    rengas = Rengas(["a", "b"], 20)
    alku = [rengas.solmu(f"k{i}") for i in range(500)]
    rengas.lisaa("c")
    rengas.poista("c")
    assert [rengas.solmu(f"k{i}") for i in range(500)] == alku


def test_sanko_purske_ja_nopeus() -> None:
    aika = [0.0]
    sanko = Sanko(nopeus=2, koko=4, kello=lambda: aika[0])
    assert sum(sanko.salli() for _ in range(10)) == 4
    aika[0] = 1.0
    assert sum(sanko.salli() for _ in range(10)) == 2
    aika[0] = 0.5                     # kello peruuttaa: ei lisää merkkejä
    assert not sanko.salli()
    with pytest.raises(ValueError):
        Sanko(nopeus=0, koko=1, kello=lambda: 0.0)


def test_histogrammi_kvantiili_ja_yhdistys() -> None:
    a, b = Histogrammi([1, 2, 4]), Histogrammi([1, 2, 4])
    for v in (0.5, 1.5, 1.5, 3):
        a.havainto(v)
    b.havainto(10)
    assert a.kvantiili(0.5) == pytest.approx(1.5)   # 2/4 -> lokero 1-2
    yhdessa = a.yhdista(b)
    assert yhdessa.laskurit == [1, 2, 1, 1]
    assert yhdessa.kvantiili(1.0) == 4               # +Inf: yläraja 4
    assert math.isnan(Histogrammi([1]).kvantiili(0.5))
    with pytest.raises(ValueError):
        a.yhdista(Histogrammi([1, 2]))


def test_prometheus_muoto() -> None:
    h = Histogrammi([0.1])
    h.havainto(0.05)
    assert h.prometheus("kesto", 'r="/"') == [
        'kesto_bucket{r="/",le="0.1"} 1', 'kesto_bucket{r="/",le="+Inf"} 1',
        'kesto_sum{r="/"} 0.050000', 'kesto_count{r="/"} 1']


def test_koodi_kaantyy_ja_peittaa_jarjestyksen() -> None:
    s = random.Random(0)
    for n in [1, 2, 3, 2 ** 40 - 1, *(s.randrange(1, 2 ** 40)
                                     for _ in range(1000))]:
        k = koodi(n)
        assert len(k) == 7 and numero(k) == n
    assert koodi(1)[:3] != koodi(2)[:3]
    for huono in ("", "abc", "zzzzzzz", "abc-def", "12345678"):
        with pytest.raises(ValueError):
            numero(huono)
    with pytest.raises(ValueError):
        koodi(0)

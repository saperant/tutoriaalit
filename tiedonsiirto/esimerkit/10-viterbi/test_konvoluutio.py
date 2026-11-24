"""Konvoluutiokoodin ja Viterbi-dekooderin testit."""

import numpy as np
import pytest
from konvoluutio import koodaa, lomita, purkulomitus, viterbi


# @alku testit
def test_tunnettu_koodisana() -> None:
    # Yksi ykkösbitti tuottaa generaattorit: 11 10 11 (impulssivaste).
    u = np.array([[1, 0, 0, 0]])
    assert koodaa(u)[0].tolist() == [1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0]


def test_vapaa_etaisyys() -> None:
    # Pienin painoinen nollasta poikkeava koodisana: paino 5.
    rng = np.random.default_rng(1)
    u = rng.integers(0, 2, (2_000, 6))
    u = u[u.any(axis=1)]
    assert koodaa(u).sum(axis=1).min() == 5


@pytest.mark.parametrize("pehmea", [False, True])
def test_kohinaton(pehmea: bool) -> None:
    rng = np.random.default_rng(2)
    u = rng.integers(0, 2, (50, 100))
    y = 1.0 - 2 * koodaa(u)
    assert np.array_equal(viterbi(y, pehmea), u)


def test_korjaa_kaksi_hajallaan_olevaa_virhetta() -> None:
    # d_free = 5: kaksi kaukana toisistaan olevaa virhettä per pätkä
    # korjautuvat kovallakin päätöksellä.
    rng = np.random.default_rng(3)
    u = rng.integers(0, 2, (100, 200))
    c = koodaa(u)
    for paikka in (10, 11, 120, 123):
        c[:, paikka] ^= 1
    assert np.array_equal(viterbi(1.0 - 2 * c, pehmea=False), u)


def test_pehmea_on_parempi_kuin_kova() -> None:
    rng = np.random.default_rng(4)
    u = rng.integers(0, 2, (200, 200))
    c = koodaa(u)
    y = 1.0 - 2 * c + 0.8 * rng.standard_normal(c.shape)
    kova = np.mean(viterbi(y, pehmea=False) != u)
    pehmea = np.mean(viterbi(y, pehmea=True) != u)
    assert pehmea < 0.5 * kova


def test_lomitus_on_kaannettavissa() -> None:
    c = np.arange(48).reshape(2, 24)
    palautettu = purkulomitus(lomita(c, 4).astype(float), 4)
    assert np.array_equal(palautettu, c)
# @loppu testit

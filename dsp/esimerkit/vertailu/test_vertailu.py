"""pytest: C-toteutukset referensseja vastaan useilla parametreilla."""

import ctypes as ct
from collections.abc import Iterator
from pathlib import Path

import numpy as np
import pytest
from scipy import signal

import kirjasto as c
from mallit import nlms, q15_prosessori, suhteellinen_ero


# @alku fixture
@pytest.fixture(scope="session")
def lib(tmp_path_factory: pytest.TempPathFactory) -> Iterator[ct.CDLL]:
    """Kirjasto kaannetaan kerran koko testiajoa varten."""
    yield c.kaanna(Path(tmp_path_factory.mktemp("c")))


@pytest.fixture
def x() -> np.ndarray:
    return np.random.default_rng(12345).standard_normal(3_000)
# @loppu fixture


# @alku fir
@pytest.mark.parametrize("lkm", [1, 2, 31, 64, 255])
@pytest.mark.parametrize("lohko", [1, 7, 256, 3_000])
def test_fir_lohkoittain(lib: ct.CDLL, x: np.ndarray, lkm: int,
                         lohko: int) -> None:
    h = signal.firwin(lkm, 0.3) if lkm > 1 else np.array([0.5])
    fir = c.Fir(lib, h)
    y = np.concatenate([fir.kasittele(x[i:i + lohko])
                        for i in range(0, x.size, lohko)])
    assert suhteellinen_ero(y, signal.lfilter(h, [1.0], x)) < 1e-12


def test_fir_hylkaa_tyhjan(lib: ct.CDLL) -> None:
    with pytest.raises(ValueError):
        c.Fir(lib, np.array([]))
# @loppu fir


# @alku sos
@pytest.mark.parametrize("aste", [2, 4, 8, 12])
@pytest.mark.parametrize("df1", [False, True])
def test_sos(lib: ct.CDLL, x: np.ndarray, aste: int, df1: bool) -> None:
    sos = signal.ellip(aste, 0.5, 70, 0.05, output="sos")
    y = c.Sos(lib, sos, df1).kasittele(x)
    assert suhteellinen_ero(y, signal.sosfilt(sos, x)) < 1e-10
# @loppu sos


@pytest.mark.parametrize("f0", [20.0, 1_000.0, 20_000.0])
def test_rbj_on_butterworth(lib: ct.CDLL, f0: float) -> None:
    viite = signal.butter(2, f0, output="sos", fs=48_000.0)[0]
    saatu = c.rbj_alipaasto(lib, f0, 2**-0.5, 48_000.0)
    assert suhteellinen_ero(saatu, viite) < 1e-10


def test_rbj_hylkaa_nyquistin(lib: ct.CDLL) -> None:
    with pytest.raises(ValueError):
        c.rbj_alipaasto(lib, 24_000.0, 0.7, 48_000.0)


# @alku fft
@pytest.mark.parametrize("n", [2, 8, 256, 4_096])
def test_fft(lib: ct.CDLL, n: int) -> None:
    rng = np.random.default_rng(n)
    z = rng.standard_normal(n) + 1j * rng.standard_normal(n)
    X = c.fft(lib, z)
    assert suhteellinen_ero(X, np.fft.fft(z)) < 1e-12
    assert suhteellinen_ero(c.fft(lib, X, kaanteinen=True), z) < 1e-12


@pytest.mark.parametrize("n", [0, 1, 6, 1_000])
def test_fft_hylkaa(lib: ct.CDLL, n: int) -> None:
    with pytest.raises(ValueError):
        c.fft(lib, np.zeros(n, dtype=np.complex128))
# @loppu fft


@pytest.mark.parametrize("M", [2, 3, 4, 8])
@pytest.mark.parametrize("lohko", [1, 5, 1_000])
def test_desimoija(lib: ct.CDLL, x: np.ndarray, M: int, lohko: int) -> None:
    h = signal.firwin(8 * M, 0.8 / M)
    d = c.Desimoija(lib, h, M)
    y = np.concatenate([d.kasittele(x[i:i + lohko])
                        for i in range(0, x.size, lohko)])
    viite = signal.upfirdn(h, x, down=M)[:y.size]
    assert y.size == -(-x.size // M)
    assert suhteellinen_ero(y, viite) < 1e-12


@pytest.mark.parametrize("L", [2, 3, 4])
def test_interpoloija(lib: ct.CDLL, x: np.ndarray, L: int) -> None:
    h = L * signal.firwin(12 * L, 0.8 / L)
    y = c.Interpoloija(lib, h, L).kasittele(x)
    viite = signal.upfirdn(h, x, up=L)[:y.size]
    assert suhteellinen_ero(y, viite) < 1e-12


def test_interpoloija_hylkaa(lib: ct.CDLL) -> None:
    with pytest.raises(ValueError):
        c.Interpoloija(lib, np.ones(10), 4)        # 10 ei ole 4:n monikerta


@pytest.mark.parametrize("mu", [0.1, 0.5, 1.0])
def test_nlms(lib: ct.CDLL, x: np.ndarray, mu: float) -> None:
    d = signal.lfilter(signal.firwin(12, 0.4), [1.0], x)
    assert suhteellinen_ero(c.nlms(lib, x, d, 12, mu),
                            nlms(x, d, 12, mu)) < 1e-9


# @alku q15
@pytest.mark.parametrize("vahvistus", [4_096, 3 * 4_096, 8 * 4_096])
def test_q15_bittitarkka(lib: ct.CDLL, x: np.ndarray,
                         vahvistus: int) -> None:
    h = np.round(signal.firwin(15, 0.25) * 32_768).astype(np.int16)
    xq = np.round(np.clip(x / 4, -1, 1) * 32_767).astype(np.int16)
    saatu, sat = c.q15_prosessori(lib, h, xq, vahvistus)
    malli, sat_malli = q15_prosessori(h, xq, vahvistus)
    np.testing.assert_array_equal(saatu, malli)
    assert sat == sat_malli
    assert (sat > 0) == (vahvistus > 4_096)
# @loppu q15

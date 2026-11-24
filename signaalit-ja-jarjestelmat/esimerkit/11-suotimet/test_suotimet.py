"""Suodinkirjaston testit: ominaisuudet, referenssit ja rajatapaukset."""

from collections.abc import Callable

import numpy as np
import pytest
from scipy import signal

from suotimet import Eksponentiaalinen, Jono, liukuva_keskiarvo, lovi


# @alku fixture
@pytest.fixture
def rng() -> np.random.Generator:
    """Kiinteä siemen: epäonnistunut testi toistuu samanlaisena."""
    return np.random.default_rng(2026)


def ema_koko(x: Jono) -> Jono:
    return Eksponentiaalinen(0.2).kasittele(x)


JARJESTELMAT: list[Callable[[Jono], Jono]] = [
    lambda x: liukuva_keskiarvo(x, 5),
    ema_koko,
]
# @loppu fixture


# @alku ominaisuudet
@pytest.mark.parametrize("T", JARJESTELMAT, ids=["keskiarvo", "ema"])
def test_lineaarisuus(T: Callable[[Jono], Jono],
                      rng: np.random.Generator) -> None:
    x1, x2 = rng.normal(size=200), rng.normal(size=200)
    np.testing.assert_allclose(T(2.0 * x1 - 3.0 * x2),
                               2.0 * T(x1) - 3.0 * T(x2), atol=1e-12)


@pytest.mark.parametrize("T", JARJESTELMAT, ids=["keskiarvo", "ema"])
@pytest.mark.parametrize("viive", [1, 7, 50])
def test_aikainvarianssi(T: Callable[[Jono], Jono], viive: int,
                         rng: np.random.Generator) -> None:
    x = rng.normal(size=200)
    siirretty = np.concatenate([np.zeros(viive), x])
    np.testing.assert_allclose(T(siirretty)[viive:], T(x), atol=1e-12)
# @loppu ominaisuudet


# @alku referenssi
def test_keskiarvo_vastaa_lfilteria(rng: np.random.Generator) -> None:
    x = rng.normal(size=300)
    odotettu = signal.lfilter(np.full(8, 1 / 8), [1.0], x)
    np.testing.assert_allclose(liukuva_keskiarvo(x, 8), odotettu,
                               rtol=0, atol=1e-12)


@pytest.mark.parametrize("lohko", [1, 3, 64, 1000])
def test_ema_lohkoittain_sama(lohko: int, rng: np.random.Generator) -> None:
    x = rng.normal(size=1000)
    kerralla = Eksponentiaalinen(0.1).kasittele(x)
    suodin = Eksponentiaalinen(0.1)
    palat = [suodin.kasittele(x[i:i + lohko])
             for i in range(0, len(x), lohko)]
    np.testing.assert_allclose(np.concatenate(palat), kerralla, atol=1e-12)
# @loppu referenssi


# @alku lovi
@pytest.mark.parametrize("f0, fs", [(50.0, 500.0), (60.0, 1000.0),
                                    (1000.0, 48000.0)])
def test_lovi(f0: float, fs: float) -> None:
    b, a = lovi(f0, fs)
    _, H = signal.freqz(b, a, worN=[0.0, f0, fs / 2 * 0.9], fs=fs)
    assert abs(H[0]) == pytest.approx(1.0, abs=1e-12)
    assert abs(H[1]) < 1e-6                       # lovi on syvä
    assert abs(H[2]) == pytest.approx(1.0, abs=0.05)   # lähes 1 muualla
    assert np.all(np.abs(np.roots(a)) < 1.0)      # stabiili


@pytest.mark.parametrize("f0", [0.0, 250.0, -5.0])
def test_lovi_hylkaa_virheellisen_taajuuden(f0: float) -> None:
    with pytest.raises(ValueError, match="ei ole välillä"):
        lovi(f0, 500.0)
# @loppu lovi

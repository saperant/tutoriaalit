"""FM-vastaanottimen osien testit: pytest -q."""

import numpy as np
import pytest
from scipy import signal

import lahetin
import rds
import vastaanotin as va


# @alku rds
def test_ehjan_lohkon_syndrooma_on_siirtymasana() -> None:
    for paikka, siirtyma in rds.SIIRTYMAT.items():
        for tieto in (0x0000, 0x6A01, 0xFFFF):
            assert rds.syndrooma(rds.lohko(tieto, paikka)) == siirtyma


def test_jokainen_yhden_bitin_virhe_havaitaan() -> None:
    sana = rds.lohko(0x6A01, "A")
    for i in range(26):
        assert rds.syndrooma(sana ^ 1 << i) != rds.SIIRTYMAT["A"]


def test_purku_loytaa_nimen_mista_tahansa_kohdasta() -> None:
    ryhmat = [rds.ryhma_0a(0x6A01, 10, "TESTI FM", k % 4)
              for k in range(9)]
    b = rds.bitit(s for r in ryhmat for s in r)
    for alku in (0, 7, 50, 103):
        tulos = rds.pura(b[alku:])
        assert tulos.pi == 0x6A01
        assert tulos.asemanimi == "TESTI FM"
# @loppu rds


# @alku osat
def test_ilmaisimen_asteikko() -> None:
    fs, poikkeama = 228e3, 75e3
    n = np.arange(1_000)
    z = np.exp(2j * np.pi * 30e3 * n / fs)    # vakiotaajuus 30 kHz
    m = va.fm_ilmaisin(z, fs, poikkeama)
    assert m == pytest.approx(np.full(len(m), 0.4))


def test_jalkikorostus_on_3_db_alas_taitetaajuudella() -> None:
    b, a = va.jalkikorostus(48e3)
    f0 = 1 / (2 * np.pi * 50e-6)               # 3183 Hz
    _, h = signal.freqz(b, a, worN=[f0], fs=48e3)
    assert 20 * np.log10(abs(h[0])) == pytest.approx(-3.0, abs=0.1)


def test_pll_loytaa_pilotin_taajuusvirheen() -> None:
    fs = 228e3
    t = np.arange(round(0.5 * fs)) / fs
    m = 0.09 * np.cos(2 * np.pi * 19_002.0 * t + 1.0)
    _, virhe_hz = va.Pll().lukitse(m, fs, 19_000.0, 19)
    assert virhe_hz == pytest.approx(2.0, abs=0.05)
# @loppu osat


# @alku ketju
def kanavaerotus(aani: va.Aani) -> float:
    a, _ = va.sinad(aani.vasen, va.FS_AANI, lahetin.VASEN_HZ)
    vuoto, _ = va.sinad(aani.vasen, va.FS_AANI, lahetin.OIKEA_HZ)
    return float(20 * np.log10(a / vuoto))


def test_sinc_korjaus_parantaa_kanavaerotusta() -> None:
    rng = np.random.default_rng(5)
    m = lahetin.mpx(0.5, "TESTI FM", 0x6A01, rng)
    z = lahetin.fm(m, lahetin.FS_MPX, lahetin.FS_IQ)
    kanava = va.valitse_kanava(z, lahetin.FS_IQ, 0.0, 4)
    mm = va.fm_ilmaisin(kanava, lahetin.FS_MPX, lahetin.POIKKEAMA)
    phi, _ = va.Pll().lukitse(mm, lahetin.FS_MPX, 19_000.0, 19)
    ilman = kanavaerotus(va.stereo(mm, phi, lahetin.FS_MPX, False))
    kanssa = kanavaerotus(va.stereo(mm, phi, lahetin.FS_MPX, True))
    assert ilman < 36 < 50 < kanssa


def test_koko_ketju_kohinassa() -> None:
    rng = np.random.default_rng(11)
    z = lahetin.tallenne(1.2, cnr_db=20.0, rng=rng)
    aani, data, _ = va.vastaanota(z, lahetin.FS_IQ, 200e3,
                                  lahetin.POIKKEAMA)
    assert data.asemanimi == "TESTI FM"
    assert kanavaerotus(aani) > 40
# @loppu ketju

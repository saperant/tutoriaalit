"""Bittitarkan mallin omat testit. Malli on RTL:n referenssi, joten sen
on oltava itse oikein: verrataan liukulukulaskentaan ja tunnettuihin
ominaisuuksiin. Ajo: pytest testit/
"""

from __future__ import annotations

import math
import random

import numpy as np
import pytest

from malli import kertoimet as k
from malli.cordic import ROTAATIO, VEKTORI, cordic, nco
from malli.kiintea import alue, kierra, kvantisoi, pyorista, saturoi, ulostulo
from malli.suotimet import biquad, cic, desimoi, fir


# @alku perus
@pytest.mark.parametrize(
    ("arvo", "odotettu"),
    [(5, 1), (6, 2), (-5, -1), (-6, -1), (-7, -2), (2, 1), (-2, 0)],
)
def test_pyoristys_puolikkaat_ylos(arvo: int, odotettu: int) -> None:
    """Siirto 2: arvo/4 pyöristettynä lähimpään, puolikkaat ylöspäin."""
    assert pyorista(arvo, 2) == odotettu


def test_saturaatio_ja_kierto() -> None:
    assert saturoi(2048, 12) == 2047
    assert saturoi(-3000, 12) == -2048
    assert kierra(2048, 12) == -2048
    assert kierra(-2049, 12) == 2047


def test_ulostulo_rajat() -> None:
    """Q2.26 -> Q1.11: täysi positiivinen ylitys saturoituu."""
    assert ulostulo(1 << 26, 15, 12) == 2047
    assert ulostulo(-(1 << 26), 15, 12) == -2048
    assert ulostulo(1 << 26, 15, 12, saturaatio=False) == -2048
    # @loppu perus


# @alku fir
def test_fir_vastaa_liukulukua() -> None:
    """Ilman saturaatiota virhe on enintään puoli LSB:tä."""
    rng = random.Random(3)
    x = [rng.randint(-1500, 1500) for _ in range(2000)]
    y = fir(x, k.FIR, k.KERROIN_MURTO, k.DATA_BITIT)
    tarkka = np.convolve(x, np.array(k.FIR) / (1 << k.KERROIN_MURTO))
    assert np.max(np.abs(np.array(y) - tarkka[: len(x)])) <= 0.5


def test_desimointi_valitsee_joka_neljannen() -> None:
    rng = random.Random(4)
    x = [rng.randint(-2048, 2047) for _ in range(400)]
    suora = fir(x, k.POLYFAASI, k.KERROIN_MURTO, k.DATA_BITIT)
    assert (
        desimoi(x, k.POLYFAASI, 4, k.KERROIN_MURTO, k.DATA_BITIT)
        == (suora[0::4])
    )
    # @loppu fir


# @alku kuollut
def test_biquad_kuollut_alue() -> None:
    """Askelvaste asettuu lähelle sisääntulon tasoa (DC-vahvistus 1).
    Takaisinkytkentä pyöristää joka näytteellä, joten tasapainoon jää
    virhe, jonka raja on 0.5 / (1 + a1 + a2) LSB."""
    *_, a1, a2 = k.SOS[0]
    raja = 0.5 * (1 << k.IIR_MURTO) / ((1 << k.IIR_MURTO) + a1 + a2)
    y = biquad([10000] * 400, k.SOS[0], k.IIR_MURTO, k.IIR_BITIT)
    assert 0 < abs(y[-1] - 10000) <= raja
    # @loppu kuollut


# @alku cic
def test_cic_kierto_ei_muuta_tulosta() -> None:
    rng = random.Random(5)
    x = [rng.randint(-2048, 2047) for _ in range(2000)]
    args = (k.CIC_ASTEET, k.CIC_DESIMOINTI, k.CIC_SISAINEN, k.CIC_ULOS)
    assert cic(x, *args, kierto=True) == cic(x, *args, kierto=False)


def test_cic_dc_vahvistus() -> None:
    """Vahvistus R**N = 512 eli 9 bittiä; ulostulosta pudotetaan 5."""
    y = cic(
        [1000] * 200,
        k.CIC_ASTEET,
        k.CIC_DESIMOINTI,
        k.CIC_SISAINEN,
        k.CIC_ULOS,
    )
    assert y[-1] == 1000 * 512 >> 5
    # @loppu cic


# @alku cordic
def test_cordic_rotaatio() -> None:
    x0 = round((1 << 15) / k.cordic_vahvistus())
    for asteet in range(-180, 180, 7):
        z = round(asteet / 360 * (1 << 16))
        x, y, _ = cordic(ROTAATIO, x0, 0, z)
        t = math.radians(asteet)
        assert abs(x / (1 << 17) - math.cos(t)) < 2e-4
        assert abs(y / (1 << 17) - math.sin(t)) < 2e-4


def test_cordic_vektori_antaa_atan2() -> None:
    for x, y in [(1000, 2000), (-30000, 5), (-7, -20000), (32767, -32768)]:
        _, yo, z = cordic(VEKTORI, x, y, 0)
        kulma = math.atan2(y, x) / (2 * math.pi) * (1 << k.CORDIC_ZW)
        ero = (z - kulma + (1 << 17)) % (1 << 18) - (1 << 17)
        assert abs(ero) < 20
        assert abs(yo) < 64  # vektori päätyy x-akselille
        # @loppu cordic


def test_nco_taulukko_ja_jakso() -> None:
    taulukko = k.nco_taulukko()
    assert taulukko == sorted(taulukko)  # kasvava neljännes
    assert max(taulukko) <= alue(k.NCO_BITIT)[1]
    y = nco(1 << (k.NCO_VAIHE - 4), 32)  # jakso 16 näytettä
    assert y[:16] == y[16:]
    assert y[:8] == [-v for v in y[8:16]]


def test_kvantisointi() -> None:
    assert kvantisoi(0.5, 15, 16) == 16384
    assert kvantisoi(1.0, 15, 16) == 32767  # +1 ei mahdu Q1.15:een
    assert kvantisoi(-1.0, 15, 16) == -32768

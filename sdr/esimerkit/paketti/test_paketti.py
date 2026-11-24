"""Pakettiradion testit: pytest -q."""

import numpy as np
import pytest

import lahetin as lh
import vastaanotin as va


# @alku kehys
def test_crc_tunnettu_tarkistusarvo() -> None:
    assert lh.crc16(b"123456789") == 0x29B1     # CRC-16/CCITT-FALSE


def test_kehyksen_rakenne() -> None:
    k = lh.kehys(b"abc")
    assert k[:4] == lh.ALKUOSA and k[4:6] == lh.TAHDISTUS
    assert k[6] == 3 and k[7:10] == b"abc" and len(k) == 12
# @loppu kehys


# @alku gfsk
def test_gfsk_vakioverhokayra_ja_taajuus() -> None:
    z = lh.gfsk([1] * 16 + [0] * 16)
    assert np.abs(z) == pytest.approx(np.ones(len(z)))
    f = np.angle(z[1:] * np.conj(z[:-1])) * lh.FS / (2 * np.pi)
    sps = round(lh.FS / lh.BITTINOPEUS)
    assert f[8 * sps] == pytest.approx(lh.POIKKEAMA, rel=1e-3)
    assert f[24 * sps] == pytest.approx(-lh.POIKKEAMA, rel=1e-3)
# @loppu gfsk


# @alku vastaanotin
@pytest.mark.parametrize("virhe", [-10e3, -2e3, 0.0, 4e3, 10e3])
def test_taajuusvirhe_korjataan(virhe: float) -> None:
    rng = np.random.default_rng(1)
    x = lh.tallenne([(0.001, b"testi", 20.0, virhe)], 0.005, 0.0, rng)
    (p,) = va.vastaanota(x, 0.0)
    assert p.crc_ok and p.data == b"testi"
    assert p.taajuusvirhe_hz == pytest.approx(virhe, abs=300)


def test_pelkassa_kohinassa_ei_vaaria_loytoja() -> None:
    x = lh.tallenne([], 0.2, 0.0, np.random.default_rng(2))
    assert va.vastaanota(x, 0.0) == []


def per(ebn0_db: float, maara: int, rng: np.random.Generator) -> float:
    virheet = 0
    for _ in range(maara):
        virhe = rng.uniform(-5e3, 5e3)
        x = lh.tallenne([(0.001, b"T=21.5C H=40%", ebn0_db, virhe)],
                        0.007, 0.0, rng)
        p = va.vastaanota(x, 0.0)
        virheet += not (len(p) == 1 and p[0].crc_ok)
    return virheet / maara


def test_pakettivirhesuhde_laskee_jyrkasti() -> None:
    rng = np.random.default_rng(3)
    assert per(8.0, 20, rng) > 0.8
    assert per(14.0, 20, rng) == 0.0
# @loppu vastaanotin

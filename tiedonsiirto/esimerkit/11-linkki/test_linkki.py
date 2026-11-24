"""Linkin testit: kohinaton kierros, rajatapaukset ja tilastollinen BER."""

import binascii

import numpy as np
import pytest
from linkki import H, Kanava, bitit, laheta, vastaanota
from scipy.special import erfc
from scipy.stats import binomtest


# @alku kohinaton
@pytest.mark.parametrize("siemen", range(20))
def test_kohinaton_kierros_satunnaisilla_virheilla(siemen: int) -> None:
    rng = np.random.default_rng(siemen)
    data = rng.integers(0, 256, 16, dtype=np.uint8).tobytes()
    kanava = Kanava(viive=int(rng.integers(0, 100)),
                    taajuus=float(rng.uniform(-2e-3, 2e-3)),
                    vaihe=float(rng.uniform(0, 2 * np.pi)))
    assert vastaanota(kanava.lapi(laheta(data), rng), 16) == data
# @loppu kohinaton


# @alku rajat
def test_lahetteen_energia_symbolia_kohti() -> None:
    data = np.random.default_rng(0).integers(0, 256, 100, dtype=np.uint8)
    x = laheta(data.tobytes())
    symboleja = 26 + 4 * 102
    assert np.sum(np.abs(x) ** 2) / symboleja == pytest.approx(1, rel=0.01)


def test_crc_havaitsee_kaannetyn_bitin() -> None:
    data = b"tiedonsiirto"
    b = bitit(data)
    b[5] ^= 1
    tavut = np.packbits(b).tobytes()
    assert binascii.crc_hqx(tavut[:-2], 0xFFFF) != int.from_bytes(
        tavut[-2:], "big")


def test_katkennut_paketti_palauttaa_none() -> None:
    rng = np.random.default_rng(1)
    x = laheta(bytes(16))[:200]
    assert vastaanota(Kanava().lapi(x, rng), 16) is None
# @loppu rajat


# @alku tilasto
def test_ber_vastaa_teoriaa_tilastollisesti() -> None:
    # Tunnetulla ajoituksella ja vaiheella bittivirheiden määrä on
    # binomijakautunut: havainto ei saa olla teorian valossa epätodennäköinen.
    rng = np.random.default_rng(5)
    EbN0_dB, tavuja = 5.0, 64
    virheita = bitteja = 0
    for _ in range(300):
        data = rng.integers(0, 256, tavuja, dtype=np.uint8).tobytes()
        z = np.convolve(Kanava(EbN0_dB=EbN0_dB).lapi(laheta(data), rng), H)
        s = z[len(H) - 1::4][26: 26 + 4 * tavuja]   # alkuosan jälkeen
        b = np.empty(2 * len(s), dtype=np.uint8)
        b[0::2], b[1::2] = s.real < 0, s.imag < 0
        lahetetyt = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
        virheita += int(np.count_nonzero(b != lahetetyt))
        bitteja += 8 * tavuja
    p = float(0.5 * erfc(np.sqrt(10 ** (EbN0_dB / 10))))
    assert binomtest(virheita, bitteja, p).pvalue > 0.001
# @loppu tilasto

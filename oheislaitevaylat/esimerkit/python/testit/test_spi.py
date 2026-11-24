"""SPI-mallin testit: moodit, ketju ja flash."""

import pytest

from mallit.spi import ketju, siirto
from mallit.spiflash import PP, RDSR, READ, WIP, WREN, SpiFlash


@pytest.mark.parametrize("moodi", range(4))
def test_sama_moodi_toimii(moodi: int) -> None:
    s = siirto([0xA5, 0x01, 0x80], [0x3C, 0xFF, 0x00], moodi)
    assert s.isannalle == [0x3C, 0xFF, 0x00]
    assert s.laitteelle == [0xA5, 0x01, 0x80]


def test_kellon_lepotaso() -> None:
    for moodi in range(4):
        sck = siirto([0x55], [0x55], moodi).aalto.signaali("SCK")
        assert sck[0] == sck[-1] == moodi >> 1


def test_vaara_vaihe_siirtaa_bitin() -> None:
    s = siirto([0xA5], [0x3C], 0, 1)
    assert s.laitteelle == [0xA5]
    assert s.isannalle == [0x9E]  # 0x3c myöhästyy bitillä


def test_ketju() -> None:
    assert ketju([1, 2, 3, 4], 3) == [4, 3, 2]


def test_flash_ohjelmointi_vaatii_wrenin() -> None:
    f = SpiFlash()
    f.transaktio(bytes([PP, 0, 0, 0]) + b"x")
    assert f.muisti[0] == 0xFF
    f.transaktio(bytes([WREN]))
    f.transaktio(bytes([PP, 0, 0, 0]) + b"x")
    assert f.transaktio(bytes([RDSR, 0]))[1] & WIP
    while f.transaktio(bytes([RDSR, 0]))[1] & WIP:
        pass
    assert f.transaktio(bytes([READ, 0, 0, 0, 0]))[4] == ord("x")


def test_flash_ohjelmointi_vain_nollaa_bitteja() -> None:
    f = SpiFlash(ohjelmointiaika=0)
    for arvo in (0xF0, 0x0F):
        f.transaktio(bytes([WREN]))
        f.transaktio(bytes([PP, 0, 0, 0, arvo]))
        f.tila = 0
    assert f.muisti[0] == 0x00

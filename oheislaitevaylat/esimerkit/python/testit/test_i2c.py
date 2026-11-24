"""I2C-mallin testit: siirrot, venytys, arbitraatio ja vapautus."""

import pytest

from mallit.i2c import Isanta, Rekisterilaite, dekoodaa, simuloi


@pytest.mark.parametrize("venytys", [0, 3, 17])
def test_rekisterin_luku_ja_kirjoitus(venytys: int) -> None:
    laite = Rekisterilaite(0x50, bytearray(range(16)), venytys)
    isanta = Isanta([(0x50, bytes([0x04, 0xAA, 0xBB]), 0),
                     (0x50, bytes([0x03]), 4)])
    aalto = simuloi([isanta, laite], 1200)
    assert isanta.loki == ["50: luettu 03 aa bb 06"]
    assert dekoodaa(aalto).startswith("S 50W A 04 A aa A bb A P")


def test_puuttuva_laite_nack() -> None:
    isanta = Isanta([(0x51, b"", 1)])
    simuloi([isanta, Rekisterilaite(0x50, bytearray(1))], 100)
    assert isanta.loki == ["51: NACK"]


def test_arbitraatio_pienempi_osoite_voittaa() -> None:
    laitteet = [Rekisterilaite(0x20, bytearray(2)),
                Rekisterilaite(0x21, bytearray(2))]
    a = Isanta([(0x21, bytes([0, 1]), 0)])
    b = Isanta([(0x20, bytes([0, 2]), 0)])
    simuloi([a, b, *laitteet], 200)
    assert a.havisi and not b.havisi
    assert laitteet[0].rekisterit[0] == 2


def test_jumiutunut_vayla_vapautuu() -> None:
    laite = Rekisterilaite(0x50, bytearray([0x00, 0x00]))
    aalto = simuloi([Isanta([(0x50, b"\x00", 1)], katkaise=135), laite],
                    150)
    assert aalto.naytteet[-1] == (1, 0)  # SDA jumissa
    uusi = Isanta([(0x50, b"\x01", 1)], vapauta=True)
    simuloi([uusi, laite], 300, aalto.osa(len(aalto.naytteet) - 1,
                                          len(aalto.naytteet)))
    assert uusi.loki[-1] == "50: luettu 00"

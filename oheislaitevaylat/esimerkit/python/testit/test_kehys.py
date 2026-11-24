"""COBS ja CRC-16: tunnetut arvot ja satunnaiset kierrokset."""

import random

import pytest

from mallit.kehys import cobs_koodaa, cobs_pura, crc16, kehys, pura_virta


def test_crc_tarkistusarvo() -> None:
    assert crc16(b"123456789") == 0x29B1  # CRC-16/CCITT-FALSE


@pytest.mark.parametrize("data, koodattu", [
    (b"", b"\x01"),
    (b"\x00", b"\x01\x01"),
    (b"\x11\x22\x00\x33", b"\x03\x11\x22\x02\x33"),
    (b"\x11\x00\x00\x00", b"\x02\x11\x01\x01\x01"),
])
def test_cobs_tunnetut(data: bytes, koodattu: bytes) -> None:
    assert cobs_koodaa(data) == koodattu
    assert cobs_pura(koodattu) == data


def test_cobs_satunnainen() -> None:
    satunnainen = random.Random(7)
    for pituus in [0, 1, 253, 254, 255, 600]:
        data = bytes(satunnainen.choice([0, 1, 255]) if pituus % 2 else
                     satunnainen.randrange(1, 256) for _ in range(pituus))
        koodattu = cobs_koodaa(data)
        assert 0 not in koodattu
        assert len(koodattu) <= len(data) + len(data) // 254 + 1
        assert cobs_pura(koodattu) == data


def test_virta_tahdistuu_virheen_jalkeen() -> None:
    virta = kehys(b"eka") + b"\x05\x01\x00" + kehys(b"toka")
    assert pura_virta(virta) == [b"eka", "virheellinen COBS", b"toka"]

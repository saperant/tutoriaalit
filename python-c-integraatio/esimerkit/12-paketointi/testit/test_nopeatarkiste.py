"""Asennetun pyöräpaketin testit: verrataan zlibiin."""

import zlib

import numpy as np
import pytest

import nopeatarkiste


@pytest.mark.parametrize("data", [b"", b"a", b"Tutoriaalit" * 1000])
def test_sama_kuin_zlib(data: bytes) -> None:
    assert nopeatarkiste.crc32(data) == zlib.crc32(data)


def test_muut_puskurit() -> None:
    data = bytes(range(256))
    odotettu = zlib.crc32(data)
    assert nopeatarkiste.crc32(bytearray(data)) == odotettu
    assert nopeatarkiste.crc32(memoryview(data)) == odotettu
    taulukko = np.frombuffer(data, dtype=np.uint8)
    assert nopeatarkiste.crc32(taulukko) == odotettu


def test_virheet() -> None:
    with pytest.raises(TypeError):
        nopeatarkiste.crc32("teksti")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="yhtenäinen"):
        nopeatarkiste.crc32(memoryview(bytes(10))[::2])

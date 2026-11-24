"""Virheiden havaitseminen: pariteetti ja CRC-32 (Ethernetin FCS)."""

import zlib

import numpy as np


def pariteetti(data: bytes) -> int:
    return sum(bin(t).count("1") for t in data) % 2


# @alku crc
def crc32(data: bytes) -> int:
    """CRC-32 bitti kerrallaan (IEEE 802.3, käännetty polynomi)."""
    crc = 0xFFFFFFFF
    for tavu in data:
        crc ^= tavu
        for _ in range(8):
            crc = (crc >> 1) ^ (0xEDB88320 if crc & 1 else 0)
    return crc ^ 0xFFFFFFFF
# @loppu crc


kehys = b"Kehyksen hyotykuorma: 46 - 1500 tavua dataa."
print(f"oma CRC-32  {crc32(kehys):08x}")
print(f"zlib.crc32  {zlib.crc32(kehys):08x}")


def kaanna_bitit(data: bytes, bitit: list[int]) -> bytes:
    muokattu = bytearray(data)
    for b in bitit:
        muokattu[b // 8] ^= 1 << (b % 8)
    return bytes(muokattu)


# @alku kokeet
rng = np.random.default_rng(7)
n_bittia = len(kehys) * 8


def yksi() -> list[int]:
    return [int(rng.integers(n_bittia))]


def kaksi() -> list[int]:
    return [int(b) for b in rng.choice(n_bittia, 2, replace=False)]


def purske() -> list[int]:
    alku = int(rng.integers(n_bittia - 32))
    return list(range(alku, alku + int(rng.integers(1, 33))))


kokeita = 2000
for nimi, virheet in [("1 bitti", yksi), ("2 bittiä", kaksi),
                      ("purske ≤ 32", purske)]:
    par = crc = 0
    for _ in range(kokeita):
        rikki = kaanna_bitit(kehys, virheet())
        par += pariteetti(rikki) != pariteetti(kehys)
        crc += crc32(rikki) != crc32(kehys)
    print(f"{nimi:<12} pariteetti havaitsi {par / kokeita:6.1%},"
          f" CRC {crc / kokeita:6.1%}")
# @loppu kokeet

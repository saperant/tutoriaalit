#!/usr/bin/env python3
"""Muuntaa P6-PPM-kuvan PNG:ksi ja suurentaa sen kokonaisluvulla.

Käyttö: python3 ppm2png.py syote.ppm tulos.png [kerroin]
Vain standardikirjasto (zlib), jotta kuvitus ei vaadi lisäpaketteja.
"""
import struct
import sys
import zlib


def lue_ppm(polku: str) -> tuple[int, int, bytes]:
    data = open(polku, "rb").read()
    osat = data.split(maxsplit=4)
    leveys, korkeus = int(osat[1]), int(osat[2])
    return leveys, korkeus, osat[4][: leveys * korkeus * 3]


def kirjoita_png(polku: str, w: int, h: int, rgb: bytes, k: int) -> None:
    rivit = bytearray()
    for y in range(h * k):
        rivi = rgb[(y // k) * w * 3:(y // k + 1) * w * 3]
        rivit.append(0)
        for x in range(w * k):
            i = (x // k) * 3
            rivit += rivi[i:i + 3]

    def lohko(tyyppi: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tyyppi + data
                + struct.pack(">I", zlib.crc32(tyyppi + data)))

    with open(polku, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(lohko(b"IHDR", struct.pack(">IIBBBBB", w * k, h * k,
                                           8, 2, 0, 0, 0)))
        f.write(lohko(b"IDAT", zlib.compress(bytes(rivit), 9)))
        f.write(lohko(b"IEND", b""))


if __name__ == "__main__":
    w, h, rgb = lue_ppm(sys.argv[1])
    kirjoita_png(sys.argv[2], w, h, rgb,
                 int(sys.argv[3]) if len(sys.argv) > 3 else 1)

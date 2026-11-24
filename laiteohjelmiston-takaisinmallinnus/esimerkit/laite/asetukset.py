"""Tehtaan työkalu: laitteen asetuslohko (256 tavua flashin lopussa).

Käyttö: python3 asetukset.py [--korjattu] kohde.bin
"""
import argparse
import struct
import zlib

import xtea

AVAIN = (0x8F2A6C11, 0x3B9D04E7, 0xC6715AF2, 0x1E48B903)
SALASANA = b"LThuolto2019"
LOHKO = 256


def huoltosalasana(salasana: bytes) -> bytes:
    selko = salasana.ljust(16, b"\0")
    tulos = b""
    for i in (0, 8):
        v0, v1 = struct.unpack_from("<II", selko, i)
        tulos += struct.pack("<II", *xtea.salaa(v0, v1, AVAIN))
    return tulos


def lohko(korjattu: bool) -> bytes:
    # Korjattu: debug-portti lukittu, ei huoltosalasanaa.
    lukitus = 0x000000CC if korjattu else 0xFFFFFFFF
    salattu = bytes(16) if korjattu else huoltosalasana(SALASANA)
    kentat = struct.pack("<IHH12siiI16s", 0x54455341, 1, 48,
                         b"LT100-04217", 66355, -35, lukitus, salattu)
    assert len(kentat) == 48
    data = kentat + struct.pack("<I", zlib.crc32(kentat))
    return data.ljust(LOHKO, b"\xff")


def main() -> None:
    jasennin = argparse.ArgumentParser()
    jasennin.add_argument("--korjattu", action="store_true")
    jasennin.add_argument("kohde")
    argumentit = jasennin.parse_args()
    with open(argumentit.kohde, "wb") as f:
        f.write(lohko(argumentit.korjattu))


if __name__ == "__main__":
    main()

"""Laitteen funktioiden ajaminen erikseen Unicornilla.

Käyttö: python3 emuloi.py FLASH

Osoitteet ovat lukujen 4-7 analyysin tuloksia. Jokainen hypoteesi
funktion tehtävästä testataan ajamalla funktio ja vertaamalla tulosta
omaan toteutukseen.
"""
import struct
import sys
import zlib

import emu

CRC32 = 0x109FC
XTEA_PURA = 0x105AC
AVAIN = 0x112B0          # 16 tavua .rodatassa, xtea_puran 2. argumentti
SALATTU = 0x3F020        # asetuslohkon 16 tavun kenttä
K_VERSIO = 0x1027C       # komentotaulun "versio"-käsittelijä
PUSKURI = 0x20008000     # vapaata RAMia argumenteille


# @alku xtea
def xtea_pura(v0: int, v1: int, k: tuple[int, ...]) -> tuple[int, int]:
    """Viitetoteutus: XTEA-purku, 32 kierrosta."""
    delta, maski = 0x9E3779B9, 0xFFFFFFFF
    summa = (delta * 32) & maski
    for _ in range(32):
        v1 = (v1 - ((((v0 << 4) ^ (v0 >> 5)) + v0)
                    ^ (summa + k[(summa >> 11) & 3]))) & maski
        summa = (summa - delta) & maski
        v0 = (v0 - ((((v1 << 4) ^ (v1 >> 5)) + v1)
                    ^ (summa + k[summa & 3]))) & maski
    return v0, v1
# @loppu xtea


def main() -> None:
    with open(sys.argv[1], "rb") as f:
        flash = f.read()
    laite = emu.Laite(flash)

    # @alku crc
    data = b"123456789"
    laite.kirjoita(PUSKURI, data)
    tulos = laite.kutsu(CRC32, PUSKURI, len(data))
    print(f"crc32: laite {tulos:08x}, zlib {zlib.crc32(data):08x}, "
          f"{laite.kaskyja} kaskya")
    tulos = laite.kutsu(CRC32, PUSKURI, len(data))
    print(f"crc32 uudelleen: {tulos:08x}, {laite.kaskyja} kaskya")
    # @loppu crc

    # @alku purku
    avain = struct.unpack("<4I", laite.lue(AVAIN, 16))
    salattu = laite.lue(SALATTU, 16)
    selko = b""
    for i in (0, 8):
        laite.kirjoita(PUSKURI, salattu[i:i + 8])
        laite.kutsu(XTEA_PURA, PUSKURI, AVAIN)
        lohko = laite.lue(PUSKURI, 8)
        v0, v1 = struct.unpack_from("<II", salattu, i)
        oma = struct.pack("<II", *xtea_pura(v0, v1, avain))
        print(f"lohko {i // 8}: laite {lohko.hex()}, viite {oma.hex()}")
        selko += lohko
    print("purettu kentta:", selko.rstrip(b"\0").decode("ascii", "replace"))
    # @loppu purku

    # @alku versio
    laite.tuloste.clear()
    paluu = laite.kutsu(K_VERSIO, 1, 0)
    print(f"k_versio palautti {paluu}, UART: {bytes(laite.tuloste)!r}")
    # @loppu versio


if __name__ == "__main__":
    main()

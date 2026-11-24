"""Algoritmien tunnistus tunnetuista vakioista.

Käyttö: python3 algoritmit.py KUVA KANTA TAULU LOPPU

Monet algoritmit käyttävät vakioita, jotka on helppo tunnistaa:
CRC-polynomit, hajautusfunktioiden alkuarvot, salainten
kierrosvakiot. Vakio kertoo, mitä funktio todennäköisesti tekee.
"""
import sys

import thumb
from kuva import Kuva

# @alku vakiot
TUNNETUT = {
    0xEDB88320: "CRC-32 (heijastettu polynomi, zlib/Ethernet)",
    0x04C11DB7: "CRC-32 (polynomi)",
    0x1021: "CRC-16/CCITT (polynomi)",
    0xA001: "CRC-16/Modbus (heijastettu polynomi)",
    0x9E3779B9: "TEA/XTEA (kierrosvakio delta)",
    0xC6EF3720: "TEA/XTEA (delta * 32)",
    0x67452301: "MD5/SHA-1 (alkuarvo)",
    0x6A09E667: "SHA-256 (alkuarvo)",
    0x5A827999: "SHA-1 (kierrosvakio)",
}
# @loppu vakiot


def main() -> None:
    kuva = Kuva.lue(sys.argv[1], int(sys.argv[2], 0))
    taulu, loppu = int(sys.argv[3], 0), int(sys.argv[4], 0)
    funktiot = thumb.kaikki_funktiot(kuva, taulu, 32, (taulu, loppu))
    for osoite, f in sorted(funktiot.items()):
        for vakio in sorted(f.vakiot & TUNNETUT.keys()):
            print(f"{osoite:#x}: {vakio:#x} {TUNNETUT[vakio]}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass

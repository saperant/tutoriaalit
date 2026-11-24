"""Tehtaan työkalu: koko flashin kuva (256 kt).

Käyttö: python3 flash.py kohde boot.bin sovellus.bin asetukset.bin M.m.p

  0x00000  käynnistyslatain
  0x10000  sovelluksen otsake (taikaluku, laite, versio, pituus, CRC)
  0x10100  sovellus
  0x3F000  asetuslohko
"""
import struct
import sys
import zlib

KOKO = 0x40000
OTSAKE, SOVELLUS, ASETUKSET = 0x10000, 0x10100, 0x3F000
LAITETUNNUS = 0x4C540064


def versio(teksti: str) -> int:
    osat = [int(osa) for osa in teksti.split(".")]
    return osat[0] << 16 | osat[1] << 8 | osat[2]


def main() -> None:
    kohde, boot, sovellus, asetukset, numero = sys.argv[1:6]
    kuva = bytearray(b"\xff" * KOKO)
    with open(boot, "rb") as f:
        data = f.read()
    kuva[:len(data)] = data
    with open(sovellus, "rb") as f:
        sov = f.read()
    otsake = struct.pack("<4sIIIII", b"LTAP", LAITETUNNUS, versio(numero),
                         len(sov), zlib.crc32(sov), 0)
    kuva[OTSAKE:OTSAKE + len(otsake)] = otsake
    kuva[SOVELLUS:SOVELLUS + len(sov)] = sov
    with open(asetukset, "rb") as f:
        aset = f.read()
    kuva[ASETUKSET:ASETUKSET + len(aset)] = aset
    with open(kohde, "wb") as f:
        f.write(kuva)


if __name__ == "__main__":
    main()

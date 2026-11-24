"""Valmistajan päivityspaketti (.lt1), jonka huoltotyökalu lataa
laitteeseen.

Käyttö: python3 pakkaa.py kohde.lt1 M.m.p sovellus.bin asetukset.bin
        ohje.txt
"""
import struct
import sys
import zlib

LAITETUNNUS = 0x4C540064
OTSAKE = struct.Struct("<4sHHIIHHIII")
OSIO = struct.Struct("<BBHIII")
EI_LADATA = 0xFFFFFFFF


def versio(teksti: str) -> int:
    osat = [int(osa) for osa in teksti.split(".")]
    return osat[0] << 16 | osat[1] << 8 | osat[2]


def main() -> None:
    kohde, numero, sovellus, asetukset, ohje = sys.argv[1:6]
    osiot: list[tuple[int, int, int, bytes, bytes]] = []
    for tyyppi, osoite, polku, pakkaa in (
            (1, 0x00010100, sovellus, False),
            (2, 0x0003F000, asetukset, False),
            (3, EI_LADATA, ohje, True)):
        with open(polku, "rb") as f:
            data = f.read()
        tallennettu = zlib.compress(data, 9) if pakkaa else data
        osiot.append((tyyppi, 1 if pakkaa else 0, osoite, data,
                      tallennettu))
    runko = b""
    for tyyppi, liput, osoite, data, tallennettu in osiot:
        runko += OSIO.pack(tyyppi, liput, 0, osoite, len(tallennettu),
                           zlib.crc32(data))
    for *_, tallennettu in osiot:
        runko += tallennettu + bytes(-len(tallennettu) % 4)
    pituus = OTSAKE.size + len(runko)

    def otsake(crc: int) -> bytes:
        return OTSAKE.pack(b"LT1P", 1, OTSAKE.size, LAITETUNNUS,
                           versio(numero), len(osiot), 0, 0, crc, pituus)

    crc = zlib.crc32(otsake(0) + runko)
    with open(kohde, "wb") as ulos:
        ulos.write(otsake(crc) + runko)


if __name__ == "__main__":
    main()

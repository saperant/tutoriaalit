"""KMTD-mittaustiedoston jäsennin, joka on kirjoitettu analyysin pohjalta.

Käyttö: python3 jasenna.py TIEDOSTO

Jäsentää otsakkeen, mittaukset ja kalibrointilohkon, tarkistaa
CRC-32-tarkisteen ja kirjoittaa tiedoston uudelleen jäsennetyistä
tiedoista. Jos uudelleen kirjoitettu tiedosto on tavulleen sama, muoto
on ymmärretty kokonaan: jokainen tavu on selitetty.
"""

import struct
import sys
import zlib
from dataclasses import dataclass


class Muotovirhe(Exception):
    """Tiedosto ei noudata päätellyä muotoa."""


@dataclass(frozen=True)
class Mittaus:
    aika: int
    lampotila: float
    kosteus: float
    anturi: int
    nimi: str


@dataclass(frozen=True)
class Tallenne:
    versio: int
    liput: int
    mittaukset: list[Mittaus]
    lohko: bytes


def jasenna(data: bytes) -> Tallenne:
    if len(data) < 16 or data[:4] != b"KMTD":
        raise Muotovirhe("tunniste KMTD puuttuu")
    if struct.unpack_from("<I", data, len(data) - 4)[0] != \
            zlib.crc32(data[:-4]):
        raise Muotovirhe("CRC-32 ei täsmää")
    versio, liput, maara = struct.unpack_from("<HHI", data, 4)
    kohta = 12
    mittaukset = []
    for _ in range(maara):
        aika, lampo, kosteus, anturi, pituus = struct.unpack_from(
            "<IhHBB", data, kohta)
        kohta += 10
        nimi = data[kohta:kohta + pituus].decode("ascii")
        kohta += pituus
        mittaukset.append(Mittaus(aika, lampo / 100, kosteus / 10,
                                  anturi, nimi))
    (koko,) = struct.unpack_from("<I", data, kohta)
    lohko = data[kohta + 4:kohta + 4 + koko]
    if kohta + 4 + koko + 4 != len(data):
        raise Muotovirhe("ylimääräisiä tavuja lohkon jälkeen")
    return Tallenne(versio, liput, mittaukset, lohko)


def kirjoita(t: Tallenne) -> bytes:
    osat = [b"KMTD", struct.pack("<HHI", t.versio, t.liput,
                                 len(t.mittaukset))]
    for m in t.mittaukset:
        nimi = m.nimi.encode("ascii")
        osat.append(struct.pack("<IhHBB", m.aika, round(m.lampotila * 100),
                                round(m.kosteus * 10), m.anturi, len(nimi)))
        osat.append(nimi)
    osat += [struct.pack("<I", len(t.lohko)), t.lohko]
    data = b"".join(osat)
    return data + struct.pack("<I", zlib.crc32(data))


def main() -> None:
    with open(sys.argv[1], "rb") as f:
        data = f.read()
    tallenne = jasenna(data)
    print(f"versio {tallenne.versio}, liput {tallenne.liput:#06x}, "
          f"{len(tallenne.mittaukset)} mittausta")
    for m in tallenne.mittaukset:
        print(f"  {m.aika}  anturi {m.anturi} {m.nimi:<9} "
              f"{m.lampotila:6.2f} C  {m.kosteus:5.1f} %")
    print(f"kalibrointilohko {len(tallenne.lohko)} tavua")
    sama = kirjoita(tallenne) == data
    print(f"uudelleen kirjoitettu tiedosto identtinen: "
          f"{'kyllä' if sama else 'EI'}")
    rikottu = bytearray(data)
    rikottu[20] ^= 0x01
    try:
        jasenna(bytes(rikottu))
    except Muotovirhe as virhe:
        print(f"yksi bitti muutettu: {virhe}")


if __name__ == "__main__":
    main()

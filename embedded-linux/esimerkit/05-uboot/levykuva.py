"""Tekee levykuvan, jossa on MBR-osiotaulu ja yksi Linux-osio.

Osion tiedostojärjestelmä tehdään erikseen komennolla
mke2fs -E offset=..., joten tämä ohjelma kirjoittaa vain osiotaulun.
Pääkäyttäjän oikeuksia ei tarvita, ja tulos on tavulleen toistettava.

Käyttö: python3 levykuva.py levy.img koko-MiB
"""

import struct
import sys

SEKTORI = 512
ALKU = 2048  # ensimmäinen osio alkaa 1 MiB:n kohdalta


# @alku osio
def osiotietue(alku: int, pituus: int, tyyppi: int,
               aktiivinen: bool) -> bytes:
    """16 tavun osiotietue. CHS-kentät ovat nykyään merkityksettömiä,
    ja niihin kirjoitetaan "ei käytössä" -arvo 0xFFFFFE."""
    chs = b"\xfe\xff\xff"
    tila = 0x80 if aktiivinen else 0x00
    return struct.pack("<B3sB3sII", tila, chs, tyyppi, chs, alku, pituus)


def mbr(sektoreita: int) -> bytes:
    """Käynnistyssektori: koodialue nollina, osiotaulu ja tunniste 55 AA."""
    taulu = osiotietue(ALKU, sektoreita - ALKU, 0x83, True)
    taulu += bytes(16 * 3)
    return bytes(446) + taulu + b"\x55\xaa"
# @loppu osio


def main() -> int:
    if len(sys.argv) != 3:
        print("kaytto: levykuva.py levy.img koko-MiB", file=sys.stderr)
        return 2
    sektoreita = int(sys.argv[2]) * 1024 * 1024 // SEKTORI
    with open(sys.argv[1], "wb") as levy:
        levy.write(mbr(sektoreita))
        levy.truncate(sektoreita * SEKTORI)
    print(f"osio 1: alku {ALKU * SEKTORI} tavua, "
          f"{(sektoreita - ALKU) * SEKTORI // 1024} KiB, tyyppi 0x83")
    return 0


if __name__ == "__main__":
    sys.exit(main())

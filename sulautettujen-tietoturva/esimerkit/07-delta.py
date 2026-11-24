"""Delta-päivitys: siirretään vain muuttuneet lohkot.

Radioyhteys on hidas ja kallis, ja akku rajallinen. Delta-päivitys
lähettää vain erot vanhaan versioon. Laite rakentaa uuden kuvan
vanhasta ja erotiedostosta ja tarkistaa tuloksen tiivisteen ennen
asennusta: väärästä pohjasta rakennettu kuva hylätään. Tuotannossa
erotiedosto tehdään esim. bsdiff- tai detools-työkalulla, ja itse
erotiedosto on allekirjoitetun manifestin kattama.
"""

import hashlib
import random

LOHKO = 1024


# @alku delta
def tee_delta(vanha: bytes, uusi: bytes) -> list[tuple[int, bytes]]:
    """Lohkot, jotka eroavat vanhasta (tai ovat sen lopun jälkeen)."""
    erot = []
    for alku in range(0, len(uusi), LOHKO):
        lohko = uusi[alku:alku + LOHKO]
        if vanha[alku:alku + LOHKO] != lohko:
            erot.append((alku, lohko))
    return erot


def sovella(vanha: bytes, delta: list[tuple[int, bytes]],
            koko: int) -> bytes:
    uusi = bytearray(vanha[:koko].ljust(koko, b"\0"))
    for alku, lohko in delta:
        uusi[alku:alku + len(lohko)] = lohko
    return bytes(uusi)
# @loppu delta


def main() -> None:
    satunnainen = random.Random(1)
    v1 = satunnainen.randbytes(256 * 1024)
    v2 = bytearray(v1)
    for kohta in (5000, 90_000, 91_000, 200_000):   # korjatut funktiot
        v2[kohta:kohta + 40] = satunnainen.randbytes(40)
    v2 += satunnainen.randbytes(3000)               # uusi ominaisuus
    uusi = bytes(v2)
    tavoite = hashlib.sha256(uusi).hexdigest()      # manifestista

    delta = tee_delta(v1, uusi)
    siirto = sum(len(lohko) + 4 for _, lohko in delta)
    osuus = f"{100 * siirto / len(uusi):.1f}".replace(".", ",")
    print(f"Täysi kuva {len(uusi)} tavua, delta {siirto} tavua "
          f"({osuus} %)")
    tulos = sovella(v1, delta, len(uusi))
    print("Oikeasta pohjasta:",
          "tiiviste täsmää" if hashlib.sha256(tulos).hexdigest() == tavoite
          else "HYLÄTÄÄN")
    v0 = satunnainen.randbytes(len(v1))             # laite oli eri versio
    tulos = sovella(v0, delta, len(uusi))
    print("Väärästä pohjasta:",
          "tiiviste täsmää" if hashlib.sha256(tulos).hexdigest() == tavoite
          else "hylätään, ladataan täysi kuva")


if __name__ == "__main__":
    main()

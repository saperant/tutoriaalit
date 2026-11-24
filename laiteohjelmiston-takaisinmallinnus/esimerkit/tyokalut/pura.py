"""Thumb-koodin purku kommentein (Capstone).

Käyttö: python3 pura.py KUVA KANTA OSOITE [MÄÄRÄ]

Purkaa MÄÄRÄ käskyä (oletus 16) osoitteesta OSOITE ja kommentoi
literaalivarannosta luetut sanat (ja merkkijonot, joihin ne
osoittavat) sekä kutsujen kohteet.
"""
import sys

import thumb
from kuva import Kuva


# @alku kommentti
def kommentti(kuva: Kuva, k: thumb.Kasky) -> str:
    if k.lukee_pc and k.kohde is not None and kuva.sisaltaa(k.kohde, 4):
        arvo = kuva.u32(k.kohde)
        teksti = kuva.merkkijono(arvo)
        if teksti:
            teksti = teksti.replace("\n", "\\n")[:24]
            return f"; ={arvo:#x} \"{teksti}\""
        return f"; ={arvo:#x}"
    return ""
# @loppu kommentti


def main() -> None:
    kuva = Kuva.lue(sys.argv[1], int(sys.argv[2], 0))
    osoite = int(sys.argv[3], 0)
    maara = int(sys.argv[4]) if len(sys.argv) > 4 else 16
    for k in thumb.pura(kuva, osoite, maara):
        # Tavut 16-bittisinä sanoina kuten objdump: b508, f000 f82b.
        tavut = " ".join(k.tavut[i:i + 2][::-1].hex()
                         for i in range(0, k.koko, 2))
        rivi = f"{k.osoite:08x}  {tavut:<9}  {k!s:<26} {kommentti(kuva, k)}"
        print(rivi.rstrip())


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass

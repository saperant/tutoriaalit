"""Kuvan viittaukset oheislaite- ja RAM-osoitteisiin.

Käyttö: python3 oheislaitteet.py KUVA KANTA TAULU LOPPU SVD

Etsii funktiot vektoritaulusta TAULU alkaen (koodialue päättyy
osoitteeseen LOPPU) ja kerää niiden lataamat vakiot: literaalivarantojen
sanat ja mov.w/movw/movt-käskyjen arvot. Tulostaa vakiot, jotka osuvat
oheislaitealueelle (0x40000000-0x5FFFFFFF) tai ytimen
järjestelmäalueelle (0xE0000000-0xE00FFFFF), nimettyinä SVD-kuvauksen
mukaan, sekä RAM-osoitteiden (0x20000000-) vaihteluvälin ja flash-osoitteet
(alle 0x40000), jotka ovat oman koodialueen ulkopuolella. Tuntematon
vakio, jonka tavut ovat tekstiä, on todennäköisesti taikaluku.
"""
import sys
import xml.etree.ElementTree as ET
from collections import Counter

import thumb
from kuva import Kuva


# @alku svd
def rekisterit(svd: str) -> dict[int, str]:
    """Osoite -> "OHEISLAITE.REKISTERI" SVD-tiedostosta."""
    nimet = {}
    for laite in ET.parse(svd).getroot().iter("peripheral"):
        nimi = laite.findtext("name", "?")
        kanta = int(laite.findtext("baseAddress", "0"), 0)
        for rekisteri in laite.iter("register"):
            siirto = int(rekisteri.findtext("addressOffset", "0"), 0)
            nimet[kanta + siirto] = f"{nimi}.{rekisteri.findtext('name')}"
    return nimet
# @loppu svd


def selite(osoite: int, nimet: dict[int, str]) -> str:
    if osoite in nimet:
        return nimet[osoite]
    tavut = osoite.to_bytes(4, "little")
    if all(0x20 <= t < 0x7F for t in tavut):
        return f"ASCII {tavut.decode()!r}: taikaluku?"
    if osoite == 0xE000E000:
        return "System Control Space, kanta"
    return "?"


def main() -> None:
    kuva = Kuva.lue(sys.argv[1], int(sys.argv[2], 0))
    taulu, loppu = int(sys.argv[3], 0), int(sys.argv[4], 0)
    nimet = rekisterit(sys.argv[5])
    funktiot = thumb.kaikki_funktiot(kuva, taulu, 32, (taulu, loppu))
    oheis: Counter[int] = Counter()
    ram, flash = set(), set()
    for f in funktiot.values():
        for arvo in f.vakiot:
            # Flash-osoite: koodialueen ulkopuolinen arvo, joka osoittaa
            # kuvan käytettyyn (ei 0xFF) kohtaan. Näin esim. CRC-polynomi
            # 0x1021 ja maski 0xffff eivät mene osoitteista.
            if (0x100 < arvo < 0x40000 and not taulu <= arvo < loppu
                    and kuva.sisaltaa(arvo)
                    and kuva.tavut(arvo, 1) != b"\xff"):
                flash.add(arvo)
            if (0x40000000 <= arvo < 0x60000000
                    or 0xE0000000 <= arvo < 0xE0100000):
                oheis[arvo] += 1
            elif 0x20000000 <= arvo < 0x20100000:
                ram.add(arvo)
    print(f"funktioita {len(funktiot)}")
    for osoite, maara in sorted(oheis.items()):
        print(f"{osoite:#010x} {maara:2} funktiossa  {selite(osoite, nimet)}")
    if ram:
        print(f"RAM-osoitteita {len(ram)}: "
              f"{min(ram):#010x}..{max(ram):#010x}")
    if flash:
        print("muut flash-osoitteet:",
              ", ".join(f"{a:#x}" for a in sorted(flash)))


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass

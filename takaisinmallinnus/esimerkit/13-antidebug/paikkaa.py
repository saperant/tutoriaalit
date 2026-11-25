"""Paikkaa ohjelmatiedostosta funktiokutsun pois.

Käyttö: python3 paikkaa.py SISÄÄN ULOS KUTSUJA KUTSUTTAVA

Etsii funktiosta KUTSUJA suoran kutsun (call rel32, 5 tavua) funktioon
KUTSUTTAVA ja korvaa sen käskyillä xor eax,eax (31 c0) ja kolmen tavun
nop (0f 1f 00): kutsu "palauttaa" aina nollan. Muu tiedosto säilyy
ennallaan, joten osoitteet eivät muutu.

Skripti kuuluu luvun 10 kokeeseen, jonka kohde on paketin oma
esimerkkiohjelma: se näyttää, että ohjelman haltija voi aina muuttaa
tiedoston tavuja, joten suojaus ei saa nojata asiakaskoodin
tarkistukseen. Toisten ohjelmien suojausten kiertämiseen sitä ei ole
tarkoitettu.
"""

import shutil
import sys

from purku import ilman_tayttoa, osiot, pura

KORVAUS = bytes([0x31, 0xC0, 0x0F, 0x1F, 0x00])


def tiedostosiirtyma(tiedosto: str, osoite: int) -> int:
    for _, alku, siirtyma, koko in osiot(tiedosto):
        if alku <= osoite < alku + koko:
            return siirtyma + osoite - alku
    raise ValueError(f"osoite {osoite:#x} ei ole missään osiossa")


# @alku main
def main() -> None:
    sisaan, ulos, kutsuja, kutsuttava = sys.argv[1:5]
    kutsut = [k for k in ilman_tayttoa(pura(sisaan)[kutsuja])
              if k.nimi == "call" and k.kohdenimi == kutsuttava]
    if len(kutsut) != 1 or len(kutsut[0].tavut) != 5:
        sys.exit(f"odotettiin yksi 5 tavun kutsu, löytyi {len(kutsut)}")
    kohta = tiedostosiirtyma(sisaan, kutsut[0].osoite)
    shutil.copy2(sisaan, ulos)
    with open(ulos, "r+b") as f:
        f.seek(kohta)
        vanha = f.read(5)
        f.seek(kohta)
        f.write(KORVAUS)
    print(f"{kutsuja}: call {kutsuttava} ({vanha[0]:02x} + rel32) "
          f"-> {KORVAUS.hex(' ')}")
# @loppu main


if __name__ == "__main__":
    main()

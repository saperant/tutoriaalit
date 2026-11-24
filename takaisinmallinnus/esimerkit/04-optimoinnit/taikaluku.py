"""Päättelee vakiolla jakavan funktion jakajan kertoimesta ja siirroista.

Käyttö: python3 taikaluku.py OHJELMA FUNKTIO...

Kääntäjä korvaa jakolaskun x / d kertolaskulla: q = (x * M) >> s.
Skripti etsii purusta kertoimen M (imul-käskyn vakio) ja siirrot,
laskee jakajan d = 2**s / M pyöristettynä ja tarkistaa tuloksen
vertaamalla kaavaa jakolaskuun suurella joukolla arvoja. Etumerkillisen
jaon korjaus (sar 31 ja vähennys) ja etumerkittömän jaon lisäysmuoto
(sub, shr 1, add) tunnistetaan.
"""

import random
import re
import sys

from purku import Kasky, ilman_tayttoa, pura


def kaava(kaskyt: list[Kasky]) -> tuple[int, int, bool, bool]:
    """Palauttaa (M, kokonaissiirto, lisäysmuoto, etumerkillinen)."""
    kerroin = siirto = 0
    lisays = etumerkki = False
    nahty = False
    for k in kaskyt:
        if k.nimi == "imul" and (m := re.search(r",0x([0-9a-f]+)$",
                                                k.operandit)):
            kerroin = int(m.group(1), 16)
            nahty = True
        elif nahty and k.nimi in ("shr", "sar"):
            m = re.search(r",(0x[0-9a-f]+|1)$", k.operandit)
            if k.operandit.endswith(",0x1f"):
                etumerkki = True
            elif m:
                siirto += int(m.group(1), 0)
        elif k.nimi == "sar" and k.operandit.endswith(",0x1f"):
            etumerkki = True
        elif nahty and k.nimi == "sub" and not lisays and not etumerkki:
            lisays = "edi" in k.operandit.split(",")[0]
    if lisays:
        kerroin += 1 << 32
    return kerroin, siirto, lisays, etumerkki


# @alku tarkista
def tarkista(kerroin: int, siirto: int, jakaja: int,
             etumerkki: bool) -> bool:
    """Vastaako kertolaskukaava jakolaskua kaikilla testiarvoilla.

    Etumerkittömässä jaossa q = (x * M) >> s. Etumerkillisessä
    negatiiviseen tulokseen lisätään yksi (kääntäjän sar 31 ja
    vähennys), jolloin jako pyöristyy kohti nollaa kuten C:ssä.
    """
    satunnainen = random.Random(2026)
    if etumerkki:
        arvot = [-2**31, -jakaja, -1, 0, 1, jakaja, 2**31 - 1]
        arvot += [satunnainen.randrange(-2**31, 2**31)
                  for _ in range(10_000)]
        return all(((x * kerroin) >> siirto) + (x < 0)
                   == int(x / jakaja) for x in arvot)
    arvot = [0, 1, jakaja - 1, jakaja, 2**31 - 1, 2**32 - 1]
    arvot += [satunnainen.randrange(2**32) for _ in range(10_000)]
    return all((x * kerroin) >> siirto == x // jakaja for x in arvot)
# @loppu tarkista


def main() -> None:
    funktiot = pura(sys.argv[1])
    for nimi in sys.argv[2:]:
        kerroin, siirto, lisays, etumerkki = kaava(
            ilman_tayttoa(funktiot[nimi]))
        jakaja = round(2**siirto / kerroin)
        muoto = (" lisäysmuoto" if lisays else "") + \
            (" etumerkillinen" if etumerkki else "")
        tulos = "ok" if tarkista(kerroin, siirto, jakaja, etumerkki) \
            else "VIRHE"
        print(f"{nimi}: M={kerroin:#x} s={siirto}{muoto}: "
              f"x/{jakaja} {tulos}")


if __name__ == "__main__":
    main()

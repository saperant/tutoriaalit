"""Funktioiden pinonkayton vertailu prologista.

Kaytto: python3 prologi.py KUVA KANTA FUNKTIO...

Tulostaa jokaisen funktion ensimmaiset kaskyt siihen asti, kun pinoa
on varattu (sub sp, #n). Suuri pinokehys ja arvojen tallennus pinoon
rekisterien sijaan on merkki optimoimattomasta kaannoksesta.
"""
import sys

import thumb
from kuva import Kuva


def main() -> None:
    kuva = Kuva.lue(sys.argv[1], int(sys.argv[2], 0))
    for teksti in sys.argv[3:]:
        osoite = int(teksti, 0)
        print(f"{osoite:#x}:")
        for k in thumb.pura(kuva, osoite, 6):
            print(f"  {k}")
            if k.nimi.startswith("sub") and "sp" in k.operandit:
                break


if __name__ == "__main__":
    main()

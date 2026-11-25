"""Tehtävä 11-1: Sarjataulukko.

Ohjelma lukee syötteestä ottelukohtaiset pisteet, rivillä joukkue ja
pisteet puolipisteellä erotettuina. Tyhjät rivit ohitetaan.

    Ilves;3
    HIFK;1
    Ilves;1
    Kärpät;3
    HIFK;3

Se tulostaa sarjataulukon: sija, joukkue ja pisteiden summa.
Järjestys on pisteiden mukaan laskeva, tasapisteissä nimen mukaan
aakkosjärjestys.

    1. HIFK 4
    2. Ilves 4
    3. Kärpät 3

Suunnittele ensin: mitkä vaiheet, mikä tietorakenne, mitkä funktiot?
Erota laskenta (rivit -> pisteet joukkueittain -> järjestys)
syötteen luvusta ja tulostuksesta.

Tarkistus: python3 tarkista.py 11-1
"""

import sys


def main() -> int:
    rivit = sys.stdin.read().splitlines()
    print(f"Rivejä: {len(rivit)}")      # korvaa toteutuksella
    return 0


if __name__ == "__main__":
    sys.exit(main())

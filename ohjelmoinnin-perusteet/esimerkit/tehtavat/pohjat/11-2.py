"""Tehtävä 11-2: Tuntiraportti.

Ohjelma lukee syötteestä työtuntikirjauksia, rivillä päivä, tekijä ja
tunnit puolipisteellä erotettuina. Tunneissa voi olla desimaalipilkku.
Tyhjät rivit ja merkillä # alkavat kommentit ohitetaan.

    # viikko 48
    2026-11-23;Aino;7,5
    2026-11-23;Ville;6
    2026-11-24;Aino;kahdeksan
    2026-11-24;Ville
    2026-11-25;Aino;5

Tuloste: tunnit tekijöittäin aakkosjärjestyksessä, yhteissumma ja
lopuksi virheelliset rivit numeroineen. Nimi tasataan vasemmalle
kymmenen merkin levyiseksi ja tunnit oikealle kuuden merkin
levyisiksi yhdellä desimaalilla ja desimaalipilkulla.

    Aino        12,5 h
    Ville        6,0 h
    Yhteensä    18,5 h
    Rivi 4: virheellinen tuntimäärä 'kahdeksan'
    Rivi 5: odotettiin 3 kenttää, saatiin 2

Myös nolla ja negatiivinen tuntimäärä ovat virheellisiä. Etene kuten
luvun budjettiohjelmassa: esimerkit, vaiheet, tietomalli, jäsennys
reunalla, laskenta erillään ja testit osille.

Tarkistus: python3 tarkista.py 11-2
"""

import sys


def main() -> int:
    rivit = sys.stdin.read().splitlines()
    print(f"Rivejä: {len(rivit)}")      # korvaa toteutuksella
    return 0


if __name__ == "__main__":
    sys.exit(main())

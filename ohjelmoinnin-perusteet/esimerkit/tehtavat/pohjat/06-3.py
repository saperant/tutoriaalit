"""Tehtävä 06-3: Tilauksen loppusumma.

Ohjelma lukee syötteestä CSV-muotoisen tilauksen, jonka erotin on
puolipiste ja ensimmäinen rivi otsikkorivi:

    tuote;kpl;hinta_snt
    Kahvi;2;699
    Korvapuusti;4;150

Se tulostaa jokaisen rivin hinnan ja lopuksi loppusumman:

    Kahvi: 13,98 €
    Korvapuusti: 6,00 €
    Yhteensä: 19,98 €

Lue syöte csv.DictReaderilla ja tee rahan muotoilusta funktio.

Tarkistus: python3 tarkista.py 06-3
"""

import csv
import sys

lukija = csv.DictReader(sys.stdin, delimiter=";")
print("Yhteensä: ?,?? €")

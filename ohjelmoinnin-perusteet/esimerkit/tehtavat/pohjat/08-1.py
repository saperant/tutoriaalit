"""Tehtävä 08-1: Laskuri.

Kirjoita luokka Laskuri, jolla lasketaan esimerkiksi ovesta kulkevia
kävijöitä. Uuden laskurin arvo on 0.

    laskuri = Laskuri()
    laskuri.kasvata()
    laskuri.kasvata()
    laskuri.arvo      ->  2
    laskuri.nollaa()
    laskuri.arvo      ->  0

Jokaisella laskurilla on oma arvonsa.

Tarkistus: python3 tarkista.py 08-1
"""


class Laskuri:
    """Laskuri, jota kasvatetaan yksi kerrallaan."""

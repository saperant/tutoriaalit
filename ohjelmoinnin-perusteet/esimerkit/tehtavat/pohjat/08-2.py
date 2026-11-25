"""Tehtävä 08-2: Suorakulmio dataluokkana.

Kirjoita dataluokka Suorakulmio, jolla on kentät leveys ja korkeus
(float) sekä metodit pinta_ala() ja on_nelio().

    s = Suorakulmio(2.0, 3.0)
    s.pinta_ala()                        ->  6.0
    s.on_nelio()                         ->  False
    s == Suorakulmio(2.0, 3.0)           ->  True
    str(s)  ->  "Suorakulmio(leveys=2.0, korkeus=3.0)"

Vertailu ja tulostusmuoto tulevat dataluokasta; niitä ei kirjoiteta
itse.

Tarkistus: python3 tarkista.py 08-2
"""


class Suorakulmio:
    """Suorakulmio, jolla on leveys ja korkeus."""

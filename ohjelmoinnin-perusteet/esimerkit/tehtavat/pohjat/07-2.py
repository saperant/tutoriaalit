"""Tehtävä 07-2: Kelvollisten rivien summa.

Kirjoita funktio, joka saa listan tekstirivejä. Se palauttaa parin:
kokonaisluvuiksi kelpaavien rivien summan ja listan niiden rivien
numeroista (alkaen yhdestä), joita ei voitu muuntaa. Tyhjät ja
pelkkiä välilyöntejä sisältävät rivit ohitetaan; ne eivät ole
virheitä.

    summaa_kelvolliset(["1", "x", "3"])  ->  (4, [2])

Tarkistus: python3 tarkista.py 07-2
"""


def summaa_kelvolliset(rivit: list[str]) -> tuple[int, list[int]]:
    """Palauttaa summan ja virheellisten rivien numerot."""
    summa = 0
    for rivi in rivit:
        summa += int(rivi)      # kaatuu virheelliseen riviin
    return summa, []

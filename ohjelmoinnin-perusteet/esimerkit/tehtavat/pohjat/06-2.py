"""Tehtävä 06-2: Palindromi.

Palindromi on sama luettuna alusta ja lopusta. Kirjoita funktio, joka
tunnistaa palindromin, kun kirjainkoosta, välilyönneistä ja
välimerkeistä ei välitetä. Tyhjä merkkijono on palindromi.

    on_palindromi("Saippuakauppias")  ->  True
    on_palindromi("Iso rikas sika sökösakissa kirosi.")  ->  True
    on_palindromi("kissa")            ->  False

Vihje: merkki.isalnum() kertoo, onko merkki kirjain tai numero, ja
viipale teksti[::-1] on merkkijono takaperin.

Tarkistus: python3 tarkista.py 06-2
"""


def on_palindromi(teksti: str) -> bool:
    """Kertoo, onko teksti palindromi."""
    return False    # korvaa tämä rivi

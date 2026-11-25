"""Tehtävä 07-1: Iän jäsennys.

Kirjoita funktio, joka muuntaa käyttäjän kirjoittaman iän
kokonaisluvuksi. Alun ja lopun välilyönnit sallitaan. Funktio nostaa
poikkeuksen ValueError kuvaavalla viestillä, jos teksti ei ole
kokonaisluku tai ikä ei ole välillä 0–150.

    jasenna_ika(" 42 ")  ->  42
    jasenna_ika("abc")   ->  ValueError
    jasenna_ika("151")   ->  ValueError

Tarkistus: python3 tarkista.py 07-1
"""

SUURIN_IKA = 150


def jasenna_ika(teksti: str) -> int:
    """Palauttaa iän kokonaislukuna tai nostaa ValueErrorin."""
    return int(teksti)      # täydennä tarkistukset

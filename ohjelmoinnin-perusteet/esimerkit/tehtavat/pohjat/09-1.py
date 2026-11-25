"""Tehtävä 09-1: Viikonpäivä.

Kirjoita funktio, joka saa päivämäärän ISO-muodossa (vvvv-kk-pp) ja
palauttaa viikonpäivän nimen suomeksi pienin kirjaimin.

    viikonpaiva("2026-11-25")  ->  "keskiviikko"

date.fromisoformat(teksti) muuntaa tekstin päivämääräksi ja nostaa
ValueErrorin, jos päivää ei ole. Anna poikkeuksen nousta kutsujalle.

Tarkistus: python3 tarkista.py 09-1
"""

from datetime import date

VIIKONPAIVAT = ["maanantai", "tiistai", "keskiviikko", "torstai",
                "perjantai", "lauantai", "sunnuntai"]


def viikonpaiva(paiva: str) -> str:
    """Palauttaa ISO-muotoisen päivämäärän viikonpäivän nimen."""
    return str(date.min)    # korvaa tämä rivi

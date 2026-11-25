"""Sääaseman lukemien käsittely.

Paketti jäsentää asemien lähettämät lukemarivit, laskee niistä
yhteenvetoja ja tarjoaa saman tiedon HTTP-rajapinnan kautta.

Moduulit:

- :mod:`saa.lukema` jäsentää rivit ja tarkistaa arvot.
- :mod:`saa.tilasto` laskee keskiarvot ja yhteenvedot.
- :mod:`saa.palvelu` on HTTP-rajapinnan käsittelijä.
"""

from saa.lukema import Lukema, LukemaVirhe, jasenna_rivi
from saa.tilasto import Yhteenveto, liukuva_keskiarvo, yhteenveto

__all__ = [
    "Lukema",
    "LukemaVirhe",
    "Yhteenveto",
    "jasenna_rivi",
    "liukuva_keskiarvo",
    "yhteenveto",
]
__version__ = "1.2.0"

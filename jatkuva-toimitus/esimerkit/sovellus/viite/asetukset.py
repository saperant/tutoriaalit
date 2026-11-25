"""Asetukset luetaan ympäristömuuttujista, ei koodista eikä paketista.

Sama artefakti toimii siksi joka ympäristössä: ympäristöjen erot ovat
muuttujissa, jotka käyttöönotto asettaa.
"""

from collections.abc import Mapping
from dataclasses import dataclass

YMPARISTOT = ("kehitys", "testi", "tuotanto")


# @alku asetukset
@dataclass(frozen=True)
class Asetukset:
    ymparisto: str = "kehitys"
    ryhmittely: bool = True


def lue(muuttujat: Mapping[str, str]) -> Asetukset:
    """Lukee asetukset ja hylkää tuntemattomat arvot heti alussa."""
    ymparisto = muuttujat.get("VIITE_YMPARISTO", "kehitys")
    if ymparisto not in YMPARISTOT:
        raise ValueError(f"tuntematon VIITE_YMPARISTO: {ymparisto!r}")
    ryhmittely = muuttujat.get("VIITE_RYHMITTELY", "1")
    if ryhmittely not in ("0", "1"):
        raise ValueError("VIITE_RYHMITTELY on 0 tai 1")
    return Asetukset(ymparisto, ryhmittely == "1")
# @loppu asetukset

"""Testien yhteiset apufunktiot: raportti ja siemen.

Testit kirjoittavat havaintonsa tiedostoon, jonka ajaja tulostaa.
cocotb:n oma loki sisältää aikaleimoja ja kestoja, joten sitä ei
verrata.
"""

from __future__ import annotations

import os
import random


def kirjaa(rivi: str) -> None:
    """Lisää rivin raporttiin (ympäristömuuttuja RAPORTTI)."""
    polku = os.environ.get("RAPORTTI")
    if polku:
        with open(polku, "a", encoding="utf-8") as f:
            f.write(rivi + "\n")


# @alku satunnainen
def satunnainen(lisa: int = 0) -> random.Random:
    """Oma satunnaislukugeneraattori siemenestä SIEMEN (+ lisa).

    Jokainen testi luo oman generaattorinsa, jotta testien järjestys
    tai lisääminen ei muuta muiden testien syötteitä.
    """
    return random.Random(int(os.environ.get("SIEMEN", "1")) + lisa)
# @loppu satunnainen

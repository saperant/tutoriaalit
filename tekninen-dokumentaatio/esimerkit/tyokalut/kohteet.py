#!/usr/bin/env python3
"""Luettelee generoidun dokumentaation kohteet.

Käyttö:  python3 tyokalut/kohteet.py sphinx POLKU/objects.inv
         python3 tyokalut/kohteet.py doxygen POLKU/xml/index.xml

Generoitua HTML:ää ei kannata verrata tavu tavulta: se muuttuu työkalun
version mukana. Kohdeluettelo sen sijaan kertoo, mitä rajapinnasta on
dokumentoitu, ja sen muutos on aina tarkoituksellinen.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path


# @alku sphinx
def sphinx(inventaario: Path) -> list[str]:
    """Lukee Sphinxin objects.inv-tiedoston Python-kohteet."""
    data = inventaario.read_bytes()
    # Neljä otsakeriviä tekstinä, loput zlib-pakattuna.
    otsake = b"".join(data.splitlines(keepends=True)[:4])
    rivit = zlib.decompress(data[len(otsake):]).decode("utf-8").splitlines()
    kohteet = []
    for rivi in rivit:
        nimi, tyyppi = rivi.split()[:2]
        if tyyppi.startswith("py:"):
            kohteet.append(f"{tyyppi[3:]:<10}{nimi}")
    return sorted(kohteet)
# @loppu sphinx


def doxygen(indeksi: Path) -> list[str]:
    """Lukee Doxygenin XML-indeksin kohteet."""
    kohteet = []
    for osa in ET.parse(indeksi).getroot().iter("compound"):
        if osa.get("kind") in ("file", "dir"):
            continue   # tiedoston jäsenet luetellaan ryhmän alla
        kohteet.append(f"{osa.get('kind', ''):<10}{osa.findtext('name')}")
        for jasen in osa.iter("member"):
            kohteet.append(f"  {jasen.get('kind', ''):<10}"
                           f"{jasen.findtext('name')}")
    return kohteet


if __name__ == "__main__":
    lukija = {"sphinx": sphinx, "doxygen": doxygen}[sys.argv[1]]
    print("\n".join(lukija(Path(sys.argv[2]))))

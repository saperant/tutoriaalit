#!/usr/bin/env python3
"""Tarkistaa dokumentteihin upotetut komentojen tulosteet.

Käyttö:  python3 tyokalut/upotukset.py [--korjaa] TIEDOSTO.md...

Markdown-tiedostossa komennon tuloste merkitään kommentilla:

    <!-- komento: python3 -m saa lukemat.csv --asema kumpula -->
    ```text
    ...
    ```

Tarkistin ajaa komennon ja vertaa tulostetta lohkon sisältöön.
Valitsin ``--korjaa`` kirjoittaa lohkon uudelleen, joten tuloste
päivitetään ajamalla työkalu eikä kopioimalla käsin.
"""

from __future__ import annotations

import re
import shlex
import subprocess
import sys
from pathlib import Path

UPOTUS = re.compile(
    r"(<!-- komento: (.+?) -->\n```\w*\n)(.*?)(```)", re.S)


def tarkista(tiedosto: Path, korjaa: bool) -> list[str]:
    """Palauttaa komennot, joiden tuloste poikkeaa dokumentista."""
    teksti = tiedosto.read_text("utf-8")
    vanhentuneet = []

    def korvaa(osuma: re.Match[str]) -> str:
        komento = osuma.group(2)
        tulos = subprocess.run(shlex.split(komento), capture_output=True,
                               text=True, check=False)
        saatu = tulos.stdout + tulos.stderr
        if saatu != osuma.group(3):
            vanhentuneet.append(komento)
        return osuma.group(1) + saatu + osuma.group(4)

    uusi = UPOTUS.sub(korvaa, teksti)
    if korjaa and uusi != teksti:
        tiedosto.write_text(uusi, "utf-8")
    return vanhentuneet


def main() -> int:
    korjaa = "--korjaa" in sys.argv
    virheita = 0
    for arg in [a for a in sys.argv[1:] if a != "--korjaa"]:
        for komento in tarkista(Path(arg), korjaa):
            sana = "päivitetty" if korjaa else "vanhentunut"
            print(f"{arg}: {sana}: {komento}")
            virheita += not korjaa
    return 1 if virheita else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Markdown-tiedostojen sisäisten linkkien tarkistin.

Käyttö:  python3 tyokalut/linkit.py HAKEMISTO_TAI_TIEDOSTO...

Tarkistaa suhteelliset linkit: kohdetiedoston on oltava olemassa, ja
jos linkissä on ankkuri (``#otsikko``), kohteessa on oltava vastaava
otsikko. Ulkoiset linkit (http, https, mailto) vain lasketaan: niiden
tarkistus vaatii verkon, joten se tehdään erikseen ajastettuna eikä
jokaisessa testiajossa.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

LINKKI = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
OTSIKKO = re.compile(r"^#{1,6}\s+(.*?)\s*#*$")
AITA = re.compile(r"^\s*(```|~~~)")


def proosarivit(tiedosto: Path) -> list[tuple[int, str]]:
    """Palauttaa rivit, jotka eivät ole koodilohkon sisällä."""
    tulos, koodissa = [], False
    for nro, rivi in enumerate(tiedosto.read_text("utf-8").splitlines(), 1):
        if AITA.match(rivi):
            koodissa = not koodissa
        elif not koodissa:
            tulos.append((nro, rivi))
    return tulos


# @alku ankkuri
def ankkuri(otsikko: str) -> str:
    """Muodostaa otsikosta ankkurin kuten GitHub.

    Kirjaimet pienennetään, välimerkit poistetaan ja välilyönnit
    korvataan yhdysmerkeillä. Muut työkalut voivat muodostaa ankkurin
    toisin: esimerkiksi MkDocs poistaa oletuksena ääkkösten pisteet.
    """
    teksti = re.sub(r"[`*_]", "", otsikko).lower()
    teksti = re.sub(r"[^\w\- ]", "", teksti)
    return teksti.replace(" ", "-")
# @loppu ankkuri


def ankkurit(tiedosto: Path) -> set[str]:
    return {ankkuri(m.group(1)) for _, rivi in proosarivit(tiedosto)
            if (m := OTSIKKO.match(rivi))}


# @alku tarkista
def tarkista(tiedosto: Path) -> tuple[list[str], int]:
    """Palauttaa tiedoston rikkinäiset linkit ja ulkoisten määrän."""
    virheet, ulkoisia = [], 0
    for nro, rivi in proosarivit(tiedosto):
        for kohde in LINKKI.findall(rivi):
            if re.match(r"^[a-z][a-z0-9+.-]*:", kohde):
                ulkoisia += 1
                continue
            polku, _, osa = kohde.partition("#")
            kohdetiedosto = (tiedosto.parent / polku) if polku else tiedosto
            if not kohdetiedosto.exists():
                virheet.append(f"{tiedosto}:{nro}: tiedostoa ei ole: "
                               f"{polku}")
            elif osa and kohdetiedosto.suffix == ".md" and \
                    osa not in ankkurit(kohdetiedosto):
                virheet.append(f"{tiedosto}:{nro}: otsikkoa ei ole: "
                               f"{kohde}")
    return virheet, ulkoisia
# @loppu tarkista


def main() -> int:
    tiedostot: list[Path] = []
    for arg in sys.argv[1:]:
        polku = Path(arg)
        tiedostot += (sorted(polku.rglob("*.md")) if polku.is_dir()
                      else [polku])
    kaikki, ulkoisia = [], 0
    for tiedosto in tiedostot:
        virheet, n = tarkista(tiedosto)
        kaikki += virheet
        ulkoisia += n
    for virhe in kaikki:
        print(virhe)
    print(f"tiedostoja {len(tiedostot)}, rikkinäisiä linkkejä {len(kaikki)}, "
          f"ulkoisia {ulkoisia} (ei tarkistettu)")
    return 1 if kaikki else 0


if __name__ == "__main__":
    sys.exit(main())

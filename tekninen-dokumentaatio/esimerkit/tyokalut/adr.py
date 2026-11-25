#!/usr/bin/env python3
"""Arkkitehtuuripäätösten (ADR) tarkistin ja hakemiston tulostaja.

Käyttö:  python3 tyokalut/adr.py HAKEMISTO

Jokainen päätös on tiedosto ``NNNN-otsikko.md``. Tarkistin varmistaa,
että numerointi on aukoton, tila on sallittu, pakolliset osiot ovat
mukana ja korvaukset viittaavat molempiin suuntiin. Lopuksi tulostetaan
hakemisto, jonka voi liittää dokumentaation etusivulle.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

TILAT = ("ehdotettu", "hyväksytty", "hylätty", "korvattu")
OSIOT = ("Tausta", "Päätös", "Seuraukset")


@dataclass
class Paatos:
    """Yhden päätöstiedoston tiedot."""

    numero: int
    otsikko: str
    tila: str
    paiva: str
    korvaa: int | None
    korvaaja: int | None
    osiot: list[str]


def lue(tiedosto: Path) -> Paatos:
    """Lukee päätöksen otsikon, kentät ja osiot."""
    teksti = tiedosto.read_text("utf-8")

    def kentta(nimi: str) -> str:
        osuma = re.search(rf"^- {nimi}: (.+)$", teksti, re.M)
        return osuma.group(1).strip() if osuma else ""

    def numero(arvo: str) -> int | None:
        osuma = re.search(r"\b(\d{4})\b", arvo)
        return int(osuma.group(1)) if osuma else None

    otsikko = re.match(r"# (\d{4})\. (.+)", teksti)
    tila = kentta("Tila")
    return Paatos(
        numero=int(otsikko.group(1)) if otsikko else -1,
        otsikko=otsikko.group(2) if otsikko else "",
        tila=tila.split()[0] if tila else "",
        paiva=kentta("Päivä"),
        korvaa=numero(kentta("Korvaa")),
        korvaaja=numero(tila) if tila.startswith("korvattu") else None,
        osiot=re.findall(r"^## (.+)$", teksti, re.M))


# @alku tarkista
def tarkista(hakemisto: Path) -> tuple[list[Paatos], list[str]]:
    """Palauttaa päätökset ja niistä löytyneet virheet."""
    tiedostot = sorted(hakemisto.glob("[0-9][0-9][0-9][0-9]-*.md"))
    paatokset, virheet = [], []
    for odotettu, tiedosto in enumerate(tiedostot, 1):
        p = lue(tiedosto)
        paatokset.append(p)
        if p.numero != odotettu or not tiedosto.name.startswith(
                f"{odotettu:04d}-"):
            virheet.append(f"{tiedosto.name}: numeron pitäisi olla "
                           f"{odotettu:04d}")
        if p.tila not in TILAT:
            virheet.append(f"{tiedosto.name}: tila '{p.tila}' ei ole "
                           f"sallittu ({', '.join(TILAT)})")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.paiva):
            virheet.append(f"{tiedosto.name}: päivä puuttuu")
        for osio in OSIOT:
            if osio not in p.osiot:
                virheet.append(f"{tiedosto.name}: osio '{osio}' puuttuu")
    numerot = {p.numero: p for p in paatokset}
    for p in paatokset:
        if p.tila == "korvattu" and (
                p.korvaaja not in numerot
                or numerot[p.korvaaja].korvaa != p.numero):
            virheet.append(f"{p.numero:04d}: korvaaja ei viittaa takaisin "
                           "(kenttä 'Korvaa')")
    return paatokset, virheet
# @loppu tarkista


def main() -> int:
    paatokset, virheet = tarkista(Path(sys.argv[1]))
    for p in paatokset:
        print(f"{p.numero:04d}  {p.paiva}  {p.tila:<10}  {p.otsikko}")
    for virhe in virheet:
        print(f"VIRHE: {virhe}")
    return 1 if virheet else 0


if __name__ == "__main__":
    sys.exit(main())

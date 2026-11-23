#!/usr/bin/env python3
"""Kielipaketin rakenteen tarkistin.

Käyttö:  python3 yhteiset/tarkista_paketti.py <paketin hakemisto>

Tarkistaa, että paketti noudattaa mallia yhteiset/KIELIPAKETTI.md:
pakolliset rungon osat löytyvät oikeilta paikoiltaan, sisältöluvut
päättyvät osioihin "Käytännössä" ja "Itsearviointi", itsearvioinnissa on
vähintään kolme osaamisväitettä ja pikaopas on olemassa.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

PAKOLLISET = [
    "johdanto", "kokeneelle", "tyypit", "ohjaus", "muisti", "kokoelmat",
    "omat-tyypit", "virheet", "modulit", "rinnakkaisuus", "tyokalut",
    "kaytannot", "lahteet",
]
KEHYS = {"johdanto", "kokeneelle", "kaytannot", "lahteet"}
MIN_VAITTEET = 3

OTSIKKO1 = re.compile(r"^# (.+?)\s*(\{([^}]*)\})?\s*$")
OTSIKKO2 = re.compile(r"^## (.+?)\s*(\{[^}]*\})?\s*$")
AITA = re.compile(r"^(```|~~~)")


@dataclass
class Luku:
    tiedosto: str
    otsikko: str
    osat: set[str]
    alaotsikot: list[str] = field(default_factory=list)
    vaitteet: int = 0


def lue_luvut(hakemisto: Path) -> tuple[list[Luku], list[str]]:
    luvut: list[Luku] = []
    virheet: list[str] = []
    for md in sorted((hakemisto / "luvut").glob("*.md")):
        koodissa = False
        nykyinen: Luku | None = None
        osio = None
        for rivi in md.read_text("utf-8").splitlines():
            if AITA.match(rivi):
                koodissa = not koodissa
                continue
            if koodissa:
                continue
            if m := OTSIKKO1.match(rivi):
                luokat = (m.group(3) or "").split()
                osat = {l[len(".runko-"):] for l in luokat
                        if l.startswith(".runko-")}
                for o in osat - set(PAKOLLISET):
                    virheet.append(f"{md.name}: tuntematon rungon osa "
                                   f"'{o}'")
                nykyinen = Luku(md.name, m.group(1), osat)
                luvut.append(nykyinen)
                osio = None
            elif (m := OTSIKKO2.match(rivi)) and nykyinen:
                osio = m.group(1).strip()
                nykyinen.alaotsikot.append(osio)
            elif osio == "Itsearviointi" and nykyinen and \
                    re.match(r"^\s*[-*]\s+Osaat\b", rivi):
                nykyinen.vaitteet += 1
    return luvut, virheet


def tarkista(hakemisto: Path) -> list[str]:
    luvut, virheet = lue_luvut(hakemisto)
    if not luvut:
        return [f"{hakemisto}: lukuja ei löytynyt"]

    loytyneet = set().union(*(l.osat for l in luvut))
    for osa in PAKOLLISET:
        if osa not in loytyneet:
            virheet.append(f"rungon osa '{osa}' puuttuu "
                           f"(merkintä {{.runko-{osa}}})")

    if "johdanto" not in luvut[0].osat:
        virheet.append(f"{luvut[0].tiedosto}: ensimmäisen luvun on oltava "
                       "johdanto")
    if len(luvut) < 2 or "kokeneelle" not in luvut[1].osat:
        virheet.append("toisen luvun on oltava kokeneelle tarkoitettu luku")
    if "lahteet" not in luvut[-1].osat:
        virheet.append(f"{luvut[-1].tiedosto}: lähteiden on oltava "
                       "viimeisessä luvussa")
    if not any("kaytannot" in l.osat for l in luvut[-2:]):
        virheet.append("käytäntöjen on oltava kahdessa viimeisessä luvussa")
    for i, l in enumerate(luvut):
        if "johdanto" in l.osat and i != 0:
            virheet.append(f"{l.tiedosto}: johdannon on oltava ensimmäinen")
        if "kokeneelle" in l.osat and i != 1:
            virheet.append(f"{l.tiedosto}: kokeneelle-luvun on oltava "
                           "toinen")

    for l in luvut:
        if l.osat & KEHYS:
            continue
        alku = f"{l.tiedosto} ({l.otsikko})"
        if l.alaotsikot[-2:] != ["Käytännössä", "Itsearviointi"]:
            virheet.append(f"{alku}: luvun on päätyttävä osioihin "
                           "'Käytännössä' ja 'Itsearviointi'")
        elif l.vaitteet < MIN_VAITTEET:
            virheet.append(f"{alku}: itsearvioinnissa on {l.vaitteet} "
                           f"osaamisväitettä, vähintään {MIN_VAITTEET}")

    if not (hakemisto / "pikaopas.md").exists():
        virheet.append("pikaopas.md puuttuu")
    return virheet


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    hakemisto = Path(sys.argv[1])
    virheet = tarkista(hakemisto)
    if virheet:
        print("\n".join(virheet))
        print(f"\nKIELIPAKETIN RAKENNE: {len(virheet)} virhettä")
        return 1
    luvut, _ = lue_luvut(hakemisto)
    print(f"OK: kielipaketin rakenne ({len(luvut)} lukua)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Tutoriaalipaketin rakenteen tarkistin.

Käyttö:  python3 yhteiset/tarkista_paketti.py [--rakenne kieli|taito] <hakemisto>

Rakenne `kieli` (oletus) tarkistaa, että kielipaketti noudattaa mallia
yhteiset/KIELIPAKETTI.md: pakolliset rungon osat löytyvät oikeilta
paikoiltaan, sisältöluvut päättyvät osioihin "Käytännössä" ja
"Itsearviointi", itsearvioinnissa on vähintään kolme osaamisväitettä ja
pikaopas on olemassa. Rungon osan voi ilmoittaa kieleen soveltumattomaksi
paketin metadata.yaml-tiedostossa:

    runko_ei_sovellu: [muisti, omat-tyypit]

Rakenne `taito` koskee muita tutoriaaleja (esim. RTL-suunnittelu, SQL):
ensimmäinen luku on johdanto ja viimeinen sisältää lähteet (merkinnät
{.runko-johdanto} ja {.runko-lahteet}), muut luvut päättyvät osioihin
"Käytännössä" ja "Itsearviointi", ja pikaopas on olemassa.
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


def ei_sovellu(hakemisto: Path) -> set[str]:
    metadata = hakemisto / "metadata.yaml"
    if not metadata.exists():
        return set()
    m = re.search(r"^runko_ei_sovellu:\s*\[([^\]]*)\]",
                  metadata.read_text("utf-8"), re.M)
    return {o.strip() for o in m.group(1).split(",")} if m else set()


def tarkista(hakemisto: Path, rakenne: str = "kieli") -> list[str]:
    luvut, virheet = lue_luvut(hakemisto)
    if not luvut:
        return [f"{hakemisto}: lukuja ei löytynyt"]

    loytyneet = set().union(*(l.osat for l in luvut))
    vaaditut = (PAKOLLISET if rakenne == "kieli"
                else ["johdanto", "lahteet"])
    poissa = ei_sovellu(hakemisto)
    for osa in poissa - set(PAKOLLISET):
        virheet.append(f"metadata.yaml: tuntematon rungon osa '{osa}'")
    for osa in vaaditut:
        if osa not in loytyneet and osa not in poissa:
            virheet.append(f"rungon osa '{osa}' puuttuu "
                           f"(merkintä {{.runko-{osa}}})")

    if "johdanto" not in luvut[0].osat:
        virheet.append(f"{luvut[0].tiedosto}: ensimmäisen luvun on oltava "
                       "johdanto")
    if rakenne == "kieli" and (len(luvut) < 2
                               or "kokeneelle" not in luvut[1].osat):
        virheet.append("toisen luvun on oltava kokeneelle tarkoitettu luku")
    if "lahteet" not in luvut[-1].osat:
        virheet.append(f"{luvut[-1].tiedosto}: lähteiden on oltava "
                       "viimeisessä luvussa")
    if rakenne == "kieli" and not any("kaytannot" in l.osat
                                      for l in luvut[-2:]):
        virheet.append("käytäntöjen on oltava kahdessa viimeisessä luvussa")
    for i, l in enumerate(luvut):
        if "johdanto" in l.osat and i != 0:
            virheet.append(f"{l.tiedosto}: johdannon on oltava ensimmäinen")
        if "kokeneelle" in l.osat and i != 1:
            virheet.append(f"{l.tiedosto}: kokeneelle-luvun on oltava "
                           "toinen")

    for i, l in enumerate(luvut):
        if l.osat & KEHYS or (rakenne == "taito"
                              and i in (0, len(luvut) - 1)):
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
    argumentit = sys.argv[1:]
    rakenne = "kieli"
    if len(argumentit) == 3 and argumentit[0] == "--rakenne":
        rakenne = argumentit[1]
        argumentit = argumentit[2:]
    if len(argumentit) != 1 or rakenne not in ("kieli", "taito"):
        print(__doc__)
        return 2
    hakemisto = Path(argumentit[0])
    virheet = tarkista(hakemisto, rakenne)
    nimi = "kielipaketin" if rakenne == "kieli" else "taitopaketin"
    if virheet:
        print("\n".join(virheet))
        print(f"\n{nimi.upper()} RAKENNE: {len(virheet)} virhettä")
        return 1
    luvut, _ = lue_luvut(hakemisto)
    print(f"OK: {nimi} rakenne ({len(luvut)} lukua)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

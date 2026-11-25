#!/usr/bin/env python3
"""Pieni proosan tarkistin teknisille dokumenteille.

Käyttö:  python3 tyokalut/proosa.py TIEDOSTO.md...

Säännöt ovat tarkoituksella harvat ja mekaaniset. Tarkistin ei tiedä,
onko teksti hyvää, mutta se huomaa asiat, jotka ihminen ohittaa
kymmenennellä lukukerralla.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from linkit import proosarivit

# @alku saannot
#: Pisin sallittu virke sanoina.
PISIN_VIRKE = 30

#: Sanat, jotka vähättelevät lukijaa tai lupaavat liikoja.
TAYTESANAT = ("yksinkertaisesti", "helposti", "tietenkin", "selvästikin",
              "triviaali")

#: Projektin sanasto: vältettävä muoto ja sen tilalle sovittu termi.
SANASTO = {
    "serveri": "palvelin",
    "logi": "loki",
    "konffi": "asetukset",
    "api-rajapinta": "rajapinta",
    "deployata": "ottaa käyttöön",
}
# @loppu saannot


def tarkista(tiedosto: Path) -> list[str]:
    """Palauttaa tiedoston huomautukset muodossa tiedosto:rivi: viesti."""
    huomiot = []

    def huomio(nro: int, viesti: str) -> None:
        huomiot.append(f"{tiedosto}:{nro}: {viesti}")

    for nro, rivi in proosarivit(tiedosto):
        pieni = rivi.lower()
        if rivi.startswith("#") and rivi.rstrip().endswith("."):
            huomio(nro, "otsikko päättyy pisteeseen")
        for sana in TAYTESANAT:
            if re.search(rf"\b{sana}", pieni):
                huomio(nro, f"täytesana '{sana}'")
        for valtettava, termi in SANASTO.items():
            if re.search(rf"\b{valtettava}", pieni):
                huomio(nro, f"käytä termiä '{termi}', ei '{valtettava}'")
        if re.search(r"\b(todo|tbd|xxx)\b", pieni):
            huomio(nro, "keskeneräisyyden merkki")
    # Virkkeet lasketaan kappaleittain, koska virke jatkuu rivin yli.
    kappale: list[tuple[int, str]] = []
    for nro, rivi in [*proosarivit(tiedosto), (0, "")]:
        if rivi.strip() and not rivi.startswith(("#", "|", "-", "<")):
            kappale.append((nro, rivi))
            continue
        teksti = " ".join(r for _, r in kappale)
        for virke in re.split(r"(?<=[.!?])\s+", teksti):
            sanoja = len(virke.split())
            if sanoja > PISIN_VIRKE:
                huomio(kappale[0][0], f"virkkeessä on {sanoja} sanaa "
                                      f"(enintään {PISIN_VIRKE})")
        kappale = []
    return sorted(huomiot, key=lambda h: int(h.split(":")[1]))


def main() -> int:
    kaikki = [h for arg in sys.argv[1:] for h in tarkista(Path(arg))]
    for h in kaikki:
        print(h)
    print(f"huomautuksia {len(kaikki)}")
    return 1 if kaikki else 0


if __name__ == "__main__":
    sys.exit(main())

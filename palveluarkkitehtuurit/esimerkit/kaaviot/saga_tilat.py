#!/usr/bin/env python3
"""Piirtää tilaussagan tilakoneen Graphviz-kaavioksi lähdekoodista.

Siirtymät luetaan orkestroijan switch-lauseesta (TilausSaga.java) ja
alkutila sekä ensimmäinen komento tilauksen aloituksesta
(Tilaukset.java). Kaavio tulostetaan vakiotulosteeseen; `make kaaviot`
vertaa sitä tallennettuun tiedostoon kaaviot/saga-tilat.dot, joten
kirjassa näkyvä kaavio vastaa aina koodia.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

MYYNTI = Path("viestit/src/main/java/fi/tutoriaalit/palvelut/viestit/myynti")

# Tilojen esitysjärjestys ja lopputilat tulevat enum-luokasta Tila.
LOPPUTILAT = {"VAHVISTETTU", "PERUTTU"}


def tilat() -> list[str]:
    """Palauttaa enum-luokan Tila arvot määrittelyjärjestyksessä."""
    lahde = (MYYNTI / "Tila.java").read_text(encoding="utf-8")
    runko = re.search(r"enum Tila \{([^}]*)\}", lahde)
    if runko is None:
        sys.exit("saga_tilat: enum Tila ei löydy")
    return [t.strip() for t in runko.group(1).split(",") if t.strip()]


def aloitus() -> tuple[str, str]:
    """Palauttaa alkutilan ja aloituksessa lähetettävän komennon."""
    lahde = (MYYNTI / "Tilaukset.java").read_text(encoding="utf-8")
    tila = re.search(r"VALUES \([^)]*'(\w+)'\)", lahde)
    komento = re.search(r'lahtevat\.lisaa\(\s*"[^"]+",\s*"(\w+)"', lahde)
    if tila is None or komento is None:
        sys.exit("saga_tilat: aloitusta ei tunnistettu")
    return tila.group(1), komento.group(1)


def siirtymat() -> list[tuple[str, str, str, str]]:
    """Palauttaa siirtymät (tila, vastaus, uusi tila, lähtevä viesti)."""
    lahde = (MYYNTI / "TilausSaga.java").read_text(encoding="utf-8")
    alku = lahde.index("switch (")
    loppu = lahde.index("default ->", alku)
    tulos = []
    for haara in lahde[alku:loppu].split("case ")[1:]:
        avain = re.match(r'"(\w+)/(\w+)"', haara)
        uusi = re.search(r"siirry\(id, Tila\.(\w+)\)", haara)
        if avain is None or uusi is None:
            sys.exit(f"saga_tilat: haaraa ei tunnistettu: {haara[:40]!r}")
        viesti = re.search(r'lahtevat\.lisaa\(\s*"[^"]+",\s*"(\w+)"', haara)
        tulos.append((avain.group(1), avain.group(2), uusi.group(1),
                      viesti.group(1) if viesti else ""))
    return tulos


def main() -> None:
    alkutila, komento = aloitus()
    print("digraph {")
    print("  rankdir=TB; nodesep=0.9; ranksep=0.45;")
    print('  alku [shape=point, width=0.12, style=filled, label=""];')
    for tila in tilat():
        lisa = ", peripheries=2" if tila in LOPPUTILAT else ""
        print(f'  {tila} [label="{tila}"{lisa}];')
    # Välilyönnit erottavat tekstin nuolesta.
    print(f'  alku -> {alkutila} '
          f'[label="  tilaus tallennettu\\l  → {komento}\\l"];')
    for tila, vastaus, uusi, viesti in siirtymat():
        nuoli = f"  → {viesti}\\l" if viesti else ""
        print(f'  {tila} -> {uusi} [label="  {vastaus}\\l{nuoli}"];')
    print("}")


if __name__ == "__main__":
    main()

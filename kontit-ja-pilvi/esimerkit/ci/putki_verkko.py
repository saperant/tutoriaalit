#!/usr/bin/env python3
"""Piirtää GitHub Actions -putken työt ja riippuvuudet Graphviz-kaavioksi.

Käyttö: putki_verkko.py ci/palvelu.yml > ci/putki.dot

Työt, niiden järjestys (needs), ehto (if) ja ympäristö (environment)
luetaan putkitiedostosta. Testi vertaa tulosta tallennettuun
kaavioon, joten kirjassa näkyvä kuva vastaa putkea.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml


def kuvaus(tyo: dict[str, Any]) -> list[str]:
    """Palauttaa työn solmuun tulevat lisärivit."""
    rivit = []
    if "refs/heads/main" in str(tyo.get("if", "")):
        rivit.append("vain päähaarasta")
    oikeudet = tyo.get("permissions", {})
    kirjoitus = sorted(k for k, v in oikeudet.items() if v == "write")
    if kirjoitus:
        rivit.append("kirjoitusoikeus: " + ", ".join(kirjoitus))
    if "environment" in tyo:
        rivit.append(f"ympäristö: {tyo['environment']}")
    return rivit


def main(polku: str) -> None:
    putki = yaml.safe_load(Path(polku).read_text("utf-8"))
    # YAML 1.1 tulkitsee avaimen "on" totuusarvoksi True.
    laukaisijat = putki.get("on", putki.get(True, {}))
    print("digraph {")
    print("  rankdir=LR; nodesep=0.3; ranksep=0.6;")
    alku = "\\n".join(str(laukaisija) for laukaisija in laukaisijat)
    print(f'  alku [label="{alku}", shape=plain, style=""];')
    for nimi, tyo in putki["jobs"].items():
        teksti = "\\n".join([nimi, *kuvaus(tyo)])
        print(f'  {nimi} [label="{teksti}"];')
    for nimi, tyo in putki["jobs"].items():
        tarpeet = tyo.get("needs", [])
        if isinstance(tarpeet, str):
            tarpeet = [tarpeet]
        if not tarpeet:
            print(f"  alku -> {nimi};")
        for tarve in tarpeet:
            print(f"  {tarve} -> {nimi};")
    print("}")


if __name__ == "__main__":
    main(sys.argv[1])

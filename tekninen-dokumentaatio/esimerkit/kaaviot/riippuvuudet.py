#!/usr/bin/env python3
"""Piirtää paketin moduulien riippuvuudet lähdekoodista.

Käyttö:  python3 kaaviot/riippuvuudet.py PAKETTI [dot|mermaid|plantuml]

Kaavio syntyy koodin import-lauseista, joten se ei voi vanhentua: kun
tuotettua tiedostoa verrataan testissä versionhallinnassa olevaan,
uusi riippuvuus näkyy katselmoinnissa muutoksena kaaviossa.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path


# @alku kaaret
def kaaret(paketti: Path) -> list[tuple[str, str]]:
    """Palauttaa paketin sisäiset riippuvuudet (tuoja, tuotu)."""
    nimi = paketti.name
    tulos = set()
    for tiedosto in sorted(paketti.glob("*.py")):
        tuoja = tiedosto.stem
        if tuoja == "__init__":
            continue   # paketin juuri vain kokoaa julkiset nimet
        for solmu in ast.walk(ast.parse(tiedosto.read_text("utf-8"))):
            if isinstance(solmu, ast.ImportFrom) and solmu.module and \
                    solmu.module.startswith(nimi + "."):
                tulos.add((tuoja, solmu.module.split(".")[1]))
            elif isinstance(solmu, ast.Import):
                tulos |= {(tuoja, a.name.split(".")[1]) for a in solmu.names
                          if a.name.startswith(nimi + ".")}
    return sorted(tulos)
# @loppu kaaret


def dot(nimi: str, k: list[tuple[str, str]]) -> str:
    rivit = [f'digraph "{nimi}" {{', "  rankdir=LR;"]
    rivit += [f'  "{a}" -> "{b}";' for a, b in k]
    return "\n".join([*rivit, "}"])


def mermaid(nimi: str, k: list[tuple[str, str]]) -> str:
    return "\n".join(["flowchart LR", *(f"  {a} --> {b}" for a, b in k)])


def plantuml(nimi: str, k: list[tuple[str, str]]) -> str:
    rivit = ["@startuml", "left to right direction"]
    rivit += [f"[{a}] --> [{b}]" for a, b in k]
    return "\n".join([*rivit, "@enduml"])


if __name__ == "__main__":
    paketti = Path(sys.argv[1])
    muoto = {"dot": dot, "mermaid": mermaid, "plantuml": plantuml}[
        sys.argv[2] if len(sys.argv) > 2 else "dot"]
    print(muoto(paketti.name, kaaret(paketti)))

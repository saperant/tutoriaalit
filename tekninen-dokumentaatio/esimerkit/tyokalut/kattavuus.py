#!/usr/bin/env python3
"""Docstringien kattavuus ja parametrien vastaavuus.

Käyttö:  python3 tyokalut/kattavuus.py HAKEMISTO_TAI_TIEDOSTO...

Tarkistaa jokaisesta Python-tiedostosta, että moduulilla ja sen
julkisilla luokilla ja funktioilla on docstring ja että docstringin
``Args:``-osio luettelee täsmälleen funktion parametrit. Paluuarvo on
1, jos puutteita löytyy.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

PARAMETRI = re.compile(r"^\s{4,8}(\*{0,2}\w+)(?: \(.*\))?:")


# @alku args
def dokumentoidut(docstring: str) -> list[str] | None:
    """Palauttaa Args-osion parametrien nimet tai None, jos osiota ei ole."""
    rivit = docstring.splitlines()
    try:
        alku = next(i for i, r in enumerate(rivit) if r.strip() == "Args:")
    except StopIteration:
        return None
    nimet = []
    sisennys = len(rivit[alku]) - len(rivit[alku].lstrip())
    for rivi in rivit[alku + 1:]:
        if rivi.strip() and len(rivi) - len(rivi.lstrip()) <= sisennys:
            break   # seuraava osio alkaa
        osuma = PARAMETRI.match(rivi[sisennys:])
        if osuma and len(rivi) - len(rivi.lstrip()) == sisennys + 4:
            nimet.append(osuma.group(1).lstrip("*"))
    return nimet
# @loppu args


def parametrit(funktio: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    a = funktio.args
    kaikki = [*a.posonlyargs, *a.args, *a.kwonlyargs]
    if a.vararg:
        kaikki.append(a.vararg)
    if a.kwarg:
        kaikki.append(a.kwarg)
    return [p.arg for p in kaikki if p.arg not in ("self", "cls")]


# @alku tarkista
def tarkista(tiedosto: Path) -> tuple[int, list[str]]:
    """Palauttaa tarkistettujen nimien määrän ja puutteet."""
    puu = ast.parse(tiedosto.read_text("utf-8"))
    maara, puutteet = 1, []
    if ast.get_docstring(puu) is None:
        puutteet.append(f"{tiedosto}:1: moduulilta puuttuu docstring")

    def kay(solmut: list[ast.stmt], etuliite: str) -> None:
        nonlocal maara
        for s in solmut:
            if not isinstance(s, ast.ClassDef | ast.FunctionDef
                              | ast.AsyncFunctionDef):
                continue
            if s.name.startswith("_"):
                continue   # yksityinen: ei kuulu rajapintaan
            maara += 1
            nimi = etuliite + s.name
            doc = ast.get_docstring(s)
            if doc is None:
                puutteet.append(f"{tiedosto}:{s.lineno}: {nimi}: "
                                "docstring puuttuu")
            elif not isinstance(s, ast.ClassDef):
                kuvatut = dokumentoidut(doc)
                oikeat = parametrit(s)
                if kuvatut is not None and kuvatut != oikeat:
                    puutteet.append(
                        f"{tiedosto}:{s.lineno}: {nimi}: Args-osiossa "
                        f"{kuvatut}, funktiossa {oikeat}")
            if isinstance(s, ast.ClassDef):
                kay(s.body, nimi + ".")

    kay(puu.body, "")
    return maara, puutteet
# @loppu tarkista


def main() -> int:
    tiedostot: list[Path] = []
    for arg in sys.argv[1:]:
        polku = Path(arg)
        tiedostot += (sorted(polku.rglob("*.py")) if polku.is_dir()
                      else [polku])
    yhteensa, kaikki = 0, []
    for tiedosto in tiedostot:
        maara, puutteet = tarkista(tiedosto)
        yhteensa += maara
        kaikki += puutteet
    for puute in kaikki:
        print(puute)
    kunnossa = yhteensa - len(kaikki)   # enintään yksi puute nimeä kohden
    print(f"dokumentoitu oikein {kunnossa}/{yhteensa} "
          f"({100 * kunnossa // max(yhteensa, 1)} %)")
    return 1 if kaikki else 0


if __name__ == "__main__":
    sys.exit(main())

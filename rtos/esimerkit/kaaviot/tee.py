#!/usr/bin/env python3
"""Tuottaa lukujen ajoituskaaviot esimerkkien testatuista tulosteista.

    python3 kaaviot/tee.py inversio testit/13-inversio.odotettu
    python3 kaaviot/tee.py rms testit/14-rms.odotettu

Tuloste on ajoituskaavion JSON (ks. yhteiset/kaaviot.py). Makefile
vertaa sitä tiedostoon kaaviot/<nimi>.json, joka näytetään kirjassa:
jos esimerkin tuloste muuttuu, kaavio on tuotettava uudelleen.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def lue(polku: str) -> tuple[list[tuple[int, str]], dict[str, str], str]:
    """Palauttaa tapahtumarivit, aikajanan rivit ja koko tekstin."""
    teksti = Path(polku).read_text(encoding="utf-8")
    tapahtumat: list[tuple[int, str]] = []
    rivit: dict[str, str] = {}
    for rivi in teksti.splitlines():
        if osuma := re.fullmatch(r"\s*(\d+) (\S.*)", rivi):
            tapahtumat.append((int(osuma[1]), osuma[2]))
        elif osuma := re.fullmatch(r"(\w+)\s+([#.]+)", rivi):
            rivit[osuma[1]] = osuma[2]
        elif osuma := re.fullmatch(r"prio\s+(\d+)  \(\w+\)", rivi):
            rivit["prio"] = osuma[1]
    return tapahtumat, rivit, teksti


def aalto(tilat: list[str]) -> tuple[str, list[str]]:
    """Tiivistää tikkikohtaiset tilat aalloksi: sama tila jatkuu pisteellä.

    Tila on joko aaltomerkki (l, x, z) tai teksti, joka piirretään
    datalaatikkona.
    """
    merkit: list[str] = []
    data: list[str] = []
    edellinen: str | None = None
    for tila in tilat:
        if tila == edellinen:
            merkit.append(".")
        elif tila in ("l", "x", "z"):
            merkit.append(tila)
        else:
            merkit.append("5" if tila == "" else "=")
            data.append(tila)
        edellinen = tila
    return "".join(merkit), data


def rivi(nimi: str, tilat: list[str]) -> dict[str, object]:
    merkit, data = aalto(tilat)
    tulos: dict[str, object] = {"name": nimi, "wave": merkit}
    if data:
        tulos["data"] = data
    return tulos


def akseli(tikkeja: int) -> dict[str, object]:
    """Aika-akseli: joka toinen tikki numeroituna."""
    return rivi("tikki", [str(t - t % 2) for t in range(tikkeja)])


def ajot(merkit: str) -> list[str]:
    return ["" if merkki == "#" else "l" for merkki in merkit]


def inversio(polku: str) -> dict[str, object]:
    tapahtumat, rivit, _ = lue(polku)
    tikkeja = len(rivit["korkea"])
    haltija = ["z"] * tikkeja
    for hetki, teksti in tapahtumat:
        if osuma := re.match(r"(\w+) (varasi|sai) vaylan", teksti):
            haltija[hetki:] = [osuma[1]] * (tikkeja - hetki)
        elif re.match(r"\w+ vapauttaa", teksti):
            haltija[hetki:] = ["z"] * (tikkeja - hetki)
    signaalit: list[object] = [akseli(tikkeja)]
    signaalit += [rivi(nimi, ajot(rivit[nimi]))
                  for nimi in ("korkea", "keski", "matala")]
    signaalit += [{}, rivi("väylän haltija", haltija),
                  rivi("matalan prioriteetti", list(rivit["prio"]))]
    return {"signal": signaalit, "config": {"hscale": 1.0}}


def rms(polku: str) -> dict[str, object]:
    """Tehtävän tila tikeittäin: odottaa julkaisua, valmiina tai ajossa."""
    _, rivit, teksti = lue(polku)
    joukko = {osuma[1]: (int(osuma[2]), int(osuma[3]))
              for osuma in re.finditer(r"^(T\d)\s+(\d+)\s+(\d+)\s", teksti,
                                       re.MULTILINE)}
    tikkeja = len(next(iter(rivit.values())))
    signaalit: list[object] = [akseli(tikkeja)]
    myohassa: dict[str, list[str]] = {}
    for nimi, merkit in rivit.items():
        tyo, jakso = joukko[nimi]
        tilat: list[str] = []
        myohassa[nimi] = []
        ajettu = 0
        for t, merkki in enumerate(merkit):
            julkaistu = (t // jakso + 1) * tyo     # työtä pyydetty tähän asti
            valmiita = ajettu // tyo               # kokonaan tehdyt työt
            myohassa[nimi].append("1" if valmiita < t // jakso else "0")
            if merkki == "#":
                tilat.append("")
                ajettu += 1
            else:
                tilat.append("x" if ajettu < julkaistu else "l")
        signaalit.append(rivi(nimi, tilat))
    for nimi, bitit in myohassa.items():
        if "1" in bitit:
            merkit = "".join(b if i == 0 or b != bitit[i - 1] else "."
                             for i, b in enumerate(bitit))
            signaalit += [{}, {"name": f"{nimi} myöhässä", "wave": merkit}]
    return {"signal": signaalit, "config": {"hscale": 0.6}}


def main() -> None:
    laji, polku = sys.argv[1], sys.argv[2]
    kaavio = {"inversio": inversio, "rms": rms}[laji](polku)
    json.dump(kaavio, sys.stdout, ensure_ascii=False, indent=1)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()

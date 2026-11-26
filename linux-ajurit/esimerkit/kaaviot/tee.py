"""Tuottaa virranhallinnan aikajanan testin tulosteesta.

    python3 kaaviot/tee.py testit/07-ajonaikainen.odotettu

Testi tulostaa anturin virtatilan (ohjelma tila) jokaisen vaiheen
jälkeen. Jokaisesta tilarivistä tulee kaavion yksi sarake, ja sarakkeen
otsikko kertoo, mitä sitä ennen tehtiin. Mukaan otetaan vaiheet osan
"jatkuva" loppuun asti. Tuloste on ajoituskaavion JSON
(ks. yhteiset/kaaviot.py). Makefile vertaa sitä tiedostoon
kaaviot/virta.json, joka näytetään kirjassa: jos testin tuloste muuttuu,
kaavio on tuotettava uudelleen.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def otsikko(komento: str) -> str | None:
    """Lyhyt nimi vaiheajurin komennolle; None, jos komentoa ei näytetä."""
    sanat = komento.split()
    if sanat[0] == "lataa":
        return "lataus"
    if sanat[0] == "poista":
        return "poisto"
    if sanat[0] == "nuku":
        return f"{int(sanat[1]) / 1000:g} s"
    if sanat[0] == "lue" and sanat[1].endswith("/paine_pa"):
        return "mittaus"
    if sanat[0] == "kirjoita":
        return f"{sanat[1].rsplit('/', 1)[1]} {sanat[2]}"
    return None


# Kaavioon otetaan testin alku tähän merkkiin asti; loput vaiheet
# (käyttäjän ohjaus ja irrotus) käsitellään tekstissä tulosteina.
LOPPU = "# @loppu jatkuva"


def lue(polku: str) -> list[tuple[str, dict[str, str]]]:
    """Palauttaa näytteet: (edeltävät vaiheet, tilarivin kentät)."""
    naytteet: list[tuple[str, dict[str, str]]] = []
    vaiheet: list[str] = []
    for rivi in Path(polku).read_text(encoding="utf-8").splitlines():
        if rivi == LOPPU:
            break
        if osuma := re.fullmatch(r"# (\w+ .*)", rivi):
            nimi = otsikko(osuma[1])
            if nimi is not None and (not vaiheet or vaiheet[-1] != nimi):
                vaiheet.append(nimi)
        elif rivi.startswith("  tila="):
            kentat = dict(kentta.split("=") for kentta in rivi.split())
            naytteet.append((", ".join(vaiheet), kentat))
            vaiheet = []
    return naytteet


def aalto(arvot: list[str], tasot: dict[str, str] | None = None
          ) -> dict[str, object]:
    """Tiivistää arvot aalloksi: sama arvo jatkuu pisteellä.

    Jos tasot on annettu, arvot piirretään viivana (0 tai 1), muuten
    nimettyinä laatikoina.
    """
    merkit: list[str] = []
    data: list[str] = []
    edellinen: str | None = None
    for arvo in arvot:
        if arvo == edellinen:
            merkit.append(".")
        elif tasot is not None:
            merkit.append(tasot[arvo])
        else:
            merkit.append("=")
            data.append(arvo)
        edellinen = arvo
    tulos: dict[str, object] = {"wave": "".join(merkit)}
    if data:
        tulos["data"] = data
    return tulos


def main() -> None:
    naytteet = lue(sys.argv[1])
    sarake = [kentat for _, kentat in naytteet]
    signaalit = [
        {"name": "vaihe",
         "wave": "=" * len(naytteet),
         "data": [vaiheet for vaiheet, _ in naytteet]},
        {"name": "runtime_status",
         **aalto([k["tila"] for k in sarake])},
        {"name": "runtime_usage",
         **aalto([k["kayttajia"] for k in sarake])},
        {"name": "vdd",
         **aalto([k["vdd"] for k in sarake],
                 {"enabled": "1", "disabled": "0"})},
        {"name": "näytekello",
         **aalto(["1" if int(k["kello"]) > 0 else "0" for k in sarake],
                 {"1": "1", "0": "0"})},
        {"name": "nreset",
         **aalto([k["nreset"] for k in sarake], {"1": "1", "0": "0"})},
    ]
    json.dump({"signal": signaalit, "config": {"hscale": 2}}, sys.stdout,
              indent=1, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()

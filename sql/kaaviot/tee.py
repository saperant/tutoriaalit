"""Tuottaa kirjan kaaviot esimerkkien testatuista tulosteista.

    python3 kaaviot/tee.py            tarkistaa kaavioiden ajantasaisuuden
    python3 kaaviot/tee.py kirjoita   kirjoittaa kaaviot uudelleen

Kaavio `11-liitossuunnitelma.dot` tehdään SQLiten kyselysuunnitelmasta
(esimerkit/11-liitossuunnitelma.odotettu): jokainen SCAN- ja
SEARCH-askel on silmukka edellisen sisällä, ja muut askeleet käsittelevät
silmukoiden tuottamat rivit.
"""

import sys
import textwrap
from pathlib import Path

JUURI = Path(__file__).resolve().parent.parent
LEVEYS = 34      # kaavion tekstirivin enimmäisleveys


def askeleet(tuloste: str) -> list[str]:
    """Poimii suunnitelman askeleet sqlite3-työkalun puutulosteesta."""
    rivit = tuloste.splitlines()
    alku = rivit.index("QUERY PLAN") + 1
    tulos = []
    for rivi in rivit[alku:]:
        if not rivi.startswith(("|--", "`--")):
            break
        tulos.append(rivi[3:])
    return tulos


def nimio(sisennys: str, avain: str, teksti: str, loppu: str = "") -> str:
    """dot-attribuutti, jonka teksti on rivitetty ja lähderivit lyhyitä."""
    osat = textwrap.wrap(teksti, LEVEYS) + ([loppu] if loppu else [])
    rivit = [f'"{osa}\\n"' for osa in osat[:-1]] + [f'"{osat[-1]}"']
    jatko = " +\n" + sisennys + " " * (len(avain) + 1)
    return f"{sisennys}{avain}={jatko.join(rivit)}"


def suunnitelma_dot(lista: list[str]) -> str:
    silmukat = [a for a in lista if a.startswith(("SCAN", "SEARCH"))]
    muut = [a for a in lista if a not in silmukat]
    ulos = ["digraph {", "  rankdir=TB; ranksep=0.35; fontsize=9;",
            "  node [fontsize=9];"]
    sis = "  "
    for nro, askel in enumerate(silmukat[:-1], start=1):
        ulos.append(f"{sis}subgraph cluster_{nro} {{")
        sis += "  "
        ulos.append(f'{sis}color="#5B6B70"; style=rounded;')
        ulos.append(nimio(sis, "label", f"{nro}. {askel}",
                          "jokaiselle riville:") + ";")
    nro = len(silmukat)
    ulos.append(f"{sis}s{nro} [")
    ulos.append(nimio(sis + "  ", "label", f"{nro}. {silmukat[-1]}") + "];")
    for _ in silmukat[:-1]:
        sis = sis[:-2]
        ulos.append(f"{sis}}}")
    edellinen = f"s{nro}"
    for i, askel in enumerate(muut, start=1):
        ulos.append(f"  m{i} [")
        ulos.append(nimio("    ", "label", askel) + "];")
        ulos.append(f'  {edellinen} -> m{i} [label=" liitetyt rivit"];')
        edellinen = f"m{i}"
    ulos.append("}")
    return "\n".join(ulos) + "\n"


def main() -> int:
    kirjoita = sys.argv[1:] == ["kirjoita"]
    lahde = JUURI / "esimerkit" / "11-liitossuunnitelma.odotettu"
    kohde = JUURI / "kaaviot" / "11-liitossuunnitelma.dot"
    uusi = suunnitelma_dot(askeleet(lahde.read_text("utf-8")))
    if kirjoita:
        kohde.write_text(uusi, "utf-8")
        return 0
    if not kohde.exists() or kohde.read_text("utf-8") != uusi:
        print(f"kaaviot: {kohde.name} ei vastaa tulostetta {lahde.name}; "
              "aja `python3 kaaviot/tee.py kirjoita`", file=sys.stderr)
        return 1
    print("OK: kaaviot vastaavat esimerkkien tulosteita")
    return 0


if __name__ == "__main__":
    sys.exit(main())

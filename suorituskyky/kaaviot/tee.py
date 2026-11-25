#!/usr/bin/env python3
"""Tuottaa luvun 4 kutsupuukaavion Callgrindin tallennetusta tulosteesta.

Käyttö:  python3 kaaviot/tee.py            kirjoittaa kaaviot/*.dot
         python3 kaaviot/tee.py --tarkista  vertaa tallennettuihin

Lähde on esimerkit/tulokset/tarkista-callgrind.txt, sama tuloste, joka
näytetään tekstissä. Solmun luku on funktion kumulatiivinen osuus
käskyistä. Kutsusuhteet (kuka kutsuu ketä) on lueteltu alla; Callgrindin
kumulatiivinen listaus ei kerro niitä, mutta ne näkyvät lähdekoodista
ja komennolla callgrind_annotate --tree=caller.
"""

import re
import sys
from pathlib import Path

JUURI = Path(__file__).resolve().parent.parent
LAHDE = JUURI / "esimerkit/tulokset/tarkista-callgrind.txt"

# Lapsi -> vanhempi. Vain nämä funktiot piirretään.
KUTSUJA = {
    "laske_hidas": "main",
    "tuota_loki": "main",
    "jasenna_sscanf": "laske_hidas",
    "etsi_lineaarisesti": "laske_hidas",
    "__isoc23_sscanf": "jasenna_sscanf",
    "__strlen_avx2": "__isoc23_sscanf",
    "__vfscanf_internal": "__isoc23_sscanf",
    "__strcmp_avx2": "etsi_lineaarisesti",
}
NIMET = {
    "__isoc23_sscanf": "sscanf",
    "__strlen_avx2": "strlen",
    "__vfscanf_internal": "vfscanf (jäsennys)",
    "__strcmp_avx2": "strcmp",
}


def osuudet() -> dict[str, float]:
    tulos: dict[str, float] = {}
    for rivi in LAHDE.read_text("utf-8").splitlines():
        m = re.match(r"\s*[\d,]+\s+([\d.]+) %\s+(\S+)", rivi)
        if m:
            tulos[m.group(2).split("@")[0]] = float(m.group(1))
    return tulos


def kutsupuu() -> str:
    o = osuudet()
    puuttuu = [f for f in ["main", *KUTSUJA] if f not in o]
    if puuttuu:
        sys.exit(f"tee.py: tulosteesta puuttuu {puuttuu}")
    rivit = ["digraph {", "  rankdir=TB; nodesep=0.3; ranksep=0.35;",
             "  node [fontsize=9];"]
    for f in ["main", *KUTSUJA]:
        osuus = f"{o[f]:.1f}".replace(".", ",")
        # Kuuma polku korostetaan: yli kolmannes käskyistä.
        tyyli = ', style="rounded,filled", fillcolor="#f3e6c8"' \
            if o[f] > 33 and f != "main" else ""
        rivit.append(f'  "{f}" [label="{NIMET.get(f, f)}\\n{osuus} %"'
                     f'{tyyli}];')
    for lapsi, vanhempi in KUTSUJA.items():
        leveys = max(0.6, o[lapsi] / 12)
        rivit.append(f'  "{vanhempi}" -> "{lapsi}" [penwidth={leveys:.1f}];')
    rivit.append("}")
    return "\n".join(rivit) + "\n"


KAAVIOT = {"04-kutsupuu.dot": kutsupuu}


def main() -> None:
    tarkista = "--tarkista" in sys.argv
    virheita = 0
    for nimi, tee in KAAVIOT.items():
        polku = JUURI / "kaaviot" / nimi
        uusi = tee()
        if not tarkista:
            polku.write_text(uusi, "utf-8")
        elif not polku.exists() or polku.read_text("utf-8") != uusi:
            print(f"VIRHE: kaaviot/{nimi} ei vastaa tallennettua tulostetta "
                  "(aja python3 kaaviot/tee.py)")
            virheita += 1
    if tarkista and not virheita:
        print(f"OK: {len(KAAVIOT)} kaavio vastaa Callgrindin tulostetta")
    sys.exit(1 if virheita else 0)


if __name__ == "__main__":
    main()

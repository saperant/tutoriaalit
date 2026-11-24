#!/usr/bin/env python3
"""Tuottaa kirjan liukuhihnakaaviot simulaattorin testatusta tulosteesta.

Käyttö:  python3 kaaviot/tee.py            kirjoittaa kaaviot/*.json
         python3 kaaviot/tee.py --tarkista  vertaa tallennettuihin

Lähde on esimerkit/04-kaavio.odotettu, jonka testi vertaa simulaattorin
tulosteeseen. Kaavio näyttää siis samat jaksot ja pysähdykset kuin
simulaattori: kukin vaihe on oma värinsä ja pysähdys viivoitettu.
"""

import json
import sys
from pathlib import Path

JUURI = Path(__file__).resolve().parent.parent
VAIHEET = {"IF": "3", "ID": "4", "EX": "5", "ME": "6", "WB": "7", "**": "x"}
SARAKE = 20      # käskyn teksti vie 20 merkkiä, jokainen jakso 3


def kaavio(rivit: list[str]) -> str:
    jaksoja = max((len(r) - SARAKE + 1) // 3 for r in rivit)
    signaalit = []
    for rivi in rivit:
        kasky = rivi[:SARAKE].strip()
        aalto = ""
        data: list[str] = []
        tyhja = False
        for j in range(jaksoja):
            solu = rivi[SARAKE + 3 * j:SARAKE + 3 * j + 2]
            if solu.strip() == "":
                aalto += "." if tyhja else "z"
                tyhja = True
                continue
            tyhja = False
            merkki = VAIHEET[solu]
            # Peräkkäiset pysähdykset yhdeksi viivoitetuksi lohkoksi.
            jatkuu = merkki == "x" and aalto.rstrip(".").endswith("x")
            aalto += "." if jatkuu else merkki
            if merkki != "x":
                data.append("MEM" if solu == "ME" else solu)
        signaalit.append({"name": kasky, "wave": aalto, "data": data})
    return json.dumps({"signal": signaalit, "config": {"hscale": 0.62}},
                      indent=1, ensure_ascii=False) + "\n"


def lohkot() -> dict[str, list[str]]:
    teksti = (JUURI / "esimerkit/04-kaavio.odotettu").read_text("utf-8")
    tulos: dict[str, list[str]] = {}
    nykyinen: list[str] = []
    for rivi in teksti.splitlines():
        if rivi.startswith("eteenpäinkytkentä"):
            nykyinen = tulos.setdefault(rivi.split(":")[0].split()[1], [])
        else:
            nykyinen.append(rivi)
    return tulos


def pois() -> str:
    return kaavio(lohkot()["pois"])


def paalla() -> str:
    return kaavio(lohkot()["päällä"])


KAAVIOT = {"04-kytkenta-pois.json": pois, "04-kytkenta-paalla.json": paalla}


def main() -> None:
    tarkista = "--tarkista" in sys.argv
    virheita = 0
    for nimi, tee in KAAVIOT.items():
        polku = JUURI / "kaaviot" / nimi
        uusi = tee()
        if not tarkista:
            polku.write_text(uusi, "utf-8")
        elif not polku.exists() or polku.read_text("utf-8") != uusi:
            print(f"VIRHE: kaaviot/{nimi} ei vastaa simulaattorin tulostetta "
                  "(aja python3 kaaviot/tee.py)")
            virheita += 1
    if tarkista and not virheita:
        print(f"OK: {len(KAAVIOT)} kaaviota vastaa simulaattorin tulostetta")
    sys.exit(1 if virheita else 0)


if __name__ == "__main__":
    main()

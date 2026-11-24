#!/usr/bin/env python3
"""Tekee vuorontajan aikajanoista ajoituskaavion (WaveDrom-JSON).

Käyttö:  python3 kaaviot/gantt.py 04-vuorontaja.odotettu > kaavio.json

Lähde on testattu tuloste, joten kaavio näyttää samat aikajanat kuin
simulaattori. Kukin prosessi saa oman värinsä (WaveDromin merkit 3-6).
"""

import json
import sys

VARIT = {"A": "3", "B": "4", "C": "5", "D": "6"}


def aalto(aikajana: str) -> tuple[str, list[str]]:
    merkit, data = "", []
    edellinen = ""
    for p in aikajana:
        if p == edellinen:
            merkit += "."
        else:
            merkit += VARIT[p]
            data.append(p)
        edellinen = p
    return merkit, data


def main() -> None:
    rivit = open(sys.argv[1], encoding="utf-8").read().splitlines()[1:]
    signaalit = []
    for rivi in rivit:
        # Nimi voi sisältää välilyönnin ("RR q=2"); aikajana on 16 merkkiä.
        osat = rivi[:8].strip(), rivi[8:].split()[0]
        merkit, data = aalto(osat[1])
        signaalit.append({"name": osat[0], "wave": merkit, "data": data})
    json.dump({"signal": signaalit}, sys.stdout, indent=1)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()

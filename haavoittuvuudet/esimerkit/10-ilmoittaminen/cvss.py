"""CVSS 3.1 -peruspisteet vektorista (FIRST: CVSS v3.1 Specification).

Käyttö:  python3 cvss.py < vektorit.txt
Jokaisella rivillä on vektori ja vapaa kuvaus, esim.
  CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N  tietovuoto
"""

from __future__ import annotations

import math
import sys

# @alku painot
AV = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}
AC = {"L": 0.77, "H": 0.44}
PR_MUUTTUMATON = {"N": 0.85, "L": 0.62, "H": 0.27}
PR_MUUTTUVA = {"N": 0.85, "L": 0.68, "H": 0.5}
UI = {"N": 0.85, "R": 0.62}
VAIKUTUS = {"H": 0.56, "L": 0.22, "N": 0.0}
# @loppu painot


def pyorista_ylos(arvo: float) -> float:
    """Spesifikaation Roundup: pienin yhden desimaalin luku >= arvo,
    laskettuna kokonaisluvuilla liukulukuvirheiden välttämiseksi."""
    kokonainen = round(arvo * 100000)
    if kokonainen % 10000 == 0:
        return kokonainen / 100000.0
    return (math.floor(kokonainen / 10000) + 1) / 10.0


# @alku pisteet
def pisteet(vektori: str) -> float:
    osat = dict(o.split(":") for o in vektori.split("/")[1:])
    muuttuva = osat["S"] == "C"
    iss = 1 - ((1 - VAIKUTUS[osat["C"]]) * (1 - VAIKUTUS[osat["I"]])
               * (1 - VAIKUTUS[osat["A"]]))
    if muuttuva:
        vaikutus = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15
    else:
        vaikutus = 6.42 * iss
    pr = (PR_MUUTTUVA if muuttuva else PR_MUUTTUMATON)[osat["PR"]]
    hyodynnettavyys = (8.22 * AV[osat["AV"]] * AC[osat["AC"]] * pr
                       * UI[osat["UI"]])
    if vaikutus <= 0:
        return 0.0
    summa = vaikutus + hyodynnettavyys
    return pyorista_ylos(min((1.08 if muuttuva else 1.0) * summa, 10))
# @loppu pisteet


def vakavuus(arvo: float) -> str:
    if arvo == 0:
        return "ei mitään"
    if arvo < 4:
        return "matala"
    if arvo < 7:
        return "keskitaso"
    if arvo < 9:
        return "korkea"
    return "kriittinen"


def main() -> int:
    for rivi in sys.stdin.read().splitlines():
        if not rivi.strip() or rivi.startswith("#"):
            continue
        vektori, _, kuvaus = rivi.partition(" ")
        arvo = pisteet(vektori)
        print(f"{arvo:4.1f} {vakavuus(arvo):<10} {kuvaus.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

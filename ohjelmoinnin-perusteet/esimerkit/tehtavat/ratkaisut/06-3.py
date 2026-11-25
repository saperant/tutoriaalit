"""Malliratkaisu 06-3: Tilauksen loppusumma."""

import csv
import sys


def euroina(sentit: int) -> str:
    """Muotoilee senttimäärän muotoon '12,34 €'."""
    return f"{sentit // 100},{sentit % 100:02d} €"


yhteensa = 0
lukija = csv.DictReader(sys.stdin, delimiter=";")
for rivi in lukija:
    hinta = int(rivi["kpl"]) * int(rivi["hinta_snt"])
    yhteensa += hinta
    print(f"{rivi['tuote']}: {euroina(hinta)}")
print(f"Yhteensä: {euroina(yhteensa)}")

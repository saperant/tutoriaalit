"""Laskee lämpötilatilastot CSV-muotoisista säähavainnoista."""

import csv
import sys

lukija = csv.DictReader(sys.stdin, delimiter=";")
lampotilat: list[float] = []
kylmin_paiva = ""
for rivi in lukija:
    lampotila = float(rivi["lampotila"].replace(",", "."))
    if not lampotilat or lampotila < min(lampotilat):
        kylmin_paiva = rivi["pvm"]
    lampotilat.append(lampotila)

keskiarvo = sum(lampotilat) / len(lampotilat)
print(f"Havaintoja {len(lampotilat)}, keskiarvo {keskiarvo:.1f} °C")
print(f"Kylmin {min(lampotilat):.1f} °C ({kylmin_paiva})")
print(f"Lämpimin {max(lampotilat):.1f} °C")

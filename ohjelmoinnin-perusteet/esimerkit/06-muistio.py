"""Tallentaa tehtäviä tekstitiedostoon ja lukee ne takaisin."""

from pathlib import Path

TIEDOSTO = Path("tehtavat.txt")

# "w" luo tiedoston tai tyhjentää olemassa olevan.
with open(TIEDOSTO, "w", encoding="utf-8") as tiedosto:
    tiedosto.write("Osta maitoa\n")
    tiedosto.write("Palauta kirjat\n")

# "a" lisää loppuun.
with open(TIEDOSTO, "a", encoding="utf-8") as tiedosto:
    print("Varaa hammaslääkäri", file=tiedosto)

with open(TIEDOSTO, encoding="utf-8") as tiedosto:
    for numero, rivi in enumerate(tiedosto, start=1):
        print(f"{numero}. {rivi.rstrip()}")

print(f"{TIEDOSTO}: {TIEDOSTO.stat().st_size} tavua")
print(TIEDOSTO.read_text(encoding="utf-8").count("\n"), "riviä")

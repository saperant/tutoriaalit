"""Ajaa komennon ja vertaa sen tulosteen odotettuun tiedostoon.

Käyttö: python3 tyokalut/vertaa.py ODOTETTU [--virhe] -- KOMENTO...

Tuloste (stdout ja stderr yhdessä) normalisoidaan: esimerkkihakemiston
absoluuttinen polku poistetaan, jotta tulos ei riipu siitä, missä
repositorio on, ja yli 78 merkin rivit taitetaan, jotta tuloste mahtuu
kirjan sivulle (jatkorivit alkavat neljällä välilyönnillä).
Valitsimella --virhe komennon on päätyttävä virheeseen (odotettu
löydös, esimerkiksi tarkoituksellinen vika); muuten sen on
onnistuttava. Ympäristömuuttuja PAIVITA=1 kirjoittaa odotetun tiedoston
uudelleen.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ESIMERKIT = Path(__file__).resolve().parent.parent
LEVEYS = 78


def taita(rivi: str) -> list[str]:
    """Jakaa pitkän rivin välilyöntien kohdalta enintään LEVEYS merkin
    paloihin."""
    palat = []
    while len(rivi) > LEVEYS:
        kohta = rivi.rfind(" ", 8, LEVEYS + 1)
        if kohta < 0:
            kohta = LEVEYS
        palat.append(rivi[:kohta].rstrip())
        rivi = "    " + rivi[kohta:].lstrip()
    return [*palat, rivi]


def normalisoi(teksti: str) -> str:
    teksti = teksti.replace(str(ESIMERKIT) + "/", "")
    rivit = [r.rstrip() for r in teksti.splitlines()]
    # Javan ja muiden työkalujen ympäristöilmoitukset eivät kuulu tulokseen.
    rivit = [r for r in rivit if not r.startswith("Picked up ")]
    rivit = [pala for r in rivit for pala in taita(r)]
    return "\n".join(rivit).strip() + "\n"


def main() -> int:
    argumentit = sys.argv[1:]
    odotettu = Path(argumentit.pop(0))
    virhe = False
    if argumentit and argumentit[0] == "--virhe":
        virhe = True
        argumentit.pop(0)
    if not argumentit or argumentit[0] != "--":
        print(__doc__)
        return 2
    komento = argumentit[1:]
    tulos = subprocess.run(
        komento, capture_output=True, text=True, check=False
    )
    saatu = normalisoi(tulos.stdout + tulos.stderr)
    nimi = odotettu.name
    if virhe and tulos.returncode == 0:
        print(f"{nimi}: komento onnistui, vaikka vika piti löytyä")
        print(saatu)
        return 1
    if not virhe and tulos.returncode != 0:
        print(f"{nimi}: komento epäonnistui (paluuarvo {tulos.returncode})")
        print(saatu)
        return 1
    if os.environ.get("PAIVITA") == "1":
        odotettu.write_text(saatu, "utf-8")
        print(f"{nimi}: päivitetty")
        return 0
    if not odotettu.exists() or odotettu.read_text("utf-8") != saatu:
        print(f"{nimi}: tuloste poikkeaa odotetusta\n--- saatu\n{saatu}")
        return 1
    print(f"OK: {nimi}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

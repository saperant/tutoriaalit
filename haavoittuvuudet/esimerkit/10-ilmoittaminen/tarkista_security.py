"""Tarkistaa security.txt-tiedoston RFC 9116:n keskeiset vaatimukset.

Käyttö:  python3 tarkista_security.py PÄIVÄYS TIEDOSTO...
PÄIVÄYS (esim. 2026-11-24) on hetki, jota vasten Expires tarkistetaan;
se annetaan argumenttina, jotta tulos on toistettava.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta

TUNNETUT = {"Acknowledgments", "Canonical", "Contact", "Encryption",
            "Expires", "Hiring", "Policy", "Preferred-Languages",
            "CSAF"}


# @alku tarkista
def tarkista(teksti: str, nyt: datetime) -> list[str]:
    kentat: dict[str, list[str]] = {}
    for rivi in teksti.splitlines():
        if not rivi.strip() or rivi.startswith("#"):
            continue
        nimi, _, arvo = rivi.partition(":")
        kentat.setdefault(nimi.strip(), []).append(arvo.strip())
    virheet = [f"tuntematon kenttä {n}" for n in kentat if n not in TUNNETUT]
    yhteydet = kentat.get("Contact", [])
    if not yhteydet:
        virheet.append("Contact puuttuu")
    for arvo in yhteydet:
        if not arvo.startswith(("mailto:", "https://", "tel:")):
            virheet.append(f"Contact ei ole URI: {arvo}")
    vanheneminen = kentat.get("Expires", [])
    if len(vanheneminen) != 1:
        virheet.append("Expires on annettava täsmälleen kerran")
    else:
        hetki = datetime.fromisoformat(vanheneminen[0])
        if hetki <= nyt:
            virheet.append("Expires on menneisyydessä")
        elif hetki - nyt > timedelta(days=366):
            virheet.append("Expires yli vuoden päässä (suositus)")
    return virheet
# @loppu tarkista


def main() -> int:
    nyt = datetime.fromisoformat(sys.argv[1]).replace(tzinfo=UTC)
    virheita = 0
    for polku in sys.argv[2:]:
        with open(polku, encoding="utf-8") as tiedosto:
            virheet = tarkista(tiedosto.read(), nyt)
        print(f"{polku}: {'ok' if not virheet else 'virheitä'}")
        for virhe in virheet:
            print(f"  {virhe}")
        virheita += len(virheet)
    return 0 if virheita == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

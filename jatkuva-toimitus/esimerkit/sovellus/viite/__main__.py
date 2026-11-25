"""Komentorivi: python3 -m viite muodosta 123456 | tarkista 1234561."""

import os
import sys
from pathlib import Path

from viite.asetukset import lue
from viite.laskenta import kelpaa, muodosta, ryhmittele


def versio() -> str:
    """Versio on rakennuksen kirjoittama tiedosto artefaktin sisällä."""
    tiedosto = Path(__file__).with_name("VERSIO")
    if tiedosto.exists():
        return tiedosto.read_text("utf-8").strip()
    return "kehitysversio"


def main(argumentit: list[str]) -> int:
    asetukset = lue(os.environ)
    match argumentit:
        case ["versio"]:
            print(f"viite {versio()} ({asetukset.ymparisto})")
        case ["muodosta", runko]:
            viite = muodosta(runko)
            print(ryhmittele(viite) if asetukset.ryhmittely else viite)
        case ["tarkista", viite]:
            print("kelpaa" if kelpaa(viite) else "ei kelpaa")
            return 0 if kelpaa(viite) else 1
        case _:
            print("käyttö: viite versio | muodosta RUNKO | tarkista VIITE",
                  file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

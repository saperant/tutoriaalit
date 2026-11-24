"""Raportin tuottaminen esimerkkituloksista."""

import json
import sys
import tempfile
from pathlib import Path

from raportti import lue, muotoile, yhteenveto


def main() -> int:
    tulokset = [
        {"testi": "uart_perus", "siemen": 1, "tila": "läpi",
         "kesto_s": 12.5},
        {"testi": "uart_perus", "siemen": 2, "tila": "läpi",
         "kesto_s": 11.75},
        {"testi": "uart_virheet", "siemen": 1, "tila": "epäonnistui",
         "kesto_s": 3.0},
    ]
    with tempfile.TemporaryDirectory() as tmp:
        polku = Path(tmp) / "tulokset.jsonl"
        polku.write_text("".join(json.dumps(t) + "\n" for t in tulokset),
                         encoding="utf-8")
        teksti = muotoile(yhteenveto(lue(polku)))
    # Ensimmäisellä rivillä on kellonaika, joka vaihtelee ajosta toiseen.
    sys.stdout.write("".join(teksti.splitlines(keepends=True)[1:]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

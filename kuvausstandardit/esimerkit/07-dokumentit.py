"""Dokumentaatio kuvauksesta: oma Markdown-generaattori ja PeakRDL:n HTML.

Markdown-dokumentti on tallennettu hakemistoon tuotettu/. HTML-sivusto
tuotetaan väliaikaiseen hakemistoon, ja sen rekisteritiedot (JSON)
verrataan malliin: dokumentin osoitteet ja kentät ovat samat kuin RTL:n
ja C-otsakkeen, koska kaikki tulevat samasta kuvauksesta.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from kuvaus.ajo import aja
from kuvaus.kaanna import RDL, TUOTETUT, kaanna
from kuvaus.malli import rekisterit


def main() -> None:
    md = (TUOTETUT / "ajastin.md").read_text("utf-8")
    print(f"ajastin.md: {md.count(chr(10) + '## ')} rekisteritaulukkoa")
    # @alku html
    with tempfile.TemporaryDirectory() as tmp:
        aja(["peakrdl", "html", str(RDL / "ajastin.rdl"), "-o", tmp])
        sivut = sorted(Path(tmp, "content").glob("*.html"))
        indeksi = "loytyi" if Path(tmp, "index.html").exists() else "PUUTTUU"
        print(f"html: index.html {indeksi}, {len(sivut)} sisaltosivua")
        solmut = json.loads(Path(tmp, "data", "ral-data-0.json")
                            .read_text("utf-8"))
    html = {(s["name"], int(s["offset"], 16),
             tuple((k["name"], k["lsb"], k["msb"]) for k in s["fields"]))
            for s in solmut if "fields" in s}
    malli = {(r.polku, r.osoite,
              tuple((k.nimi, k.lsb, k.msb) for k in r.kentat))
             for r in rekisterit(kaanna("ajastin.rdl"))}
    print(f"html ja malli: {len(html)} rekisteria, "
          f"{'samat' if html == malli else 'EROAVAT'}")
    # @loppu html


if __name__ == "__main__":
    main()

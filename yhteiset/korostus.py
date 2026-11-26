#!/usr/bin/env python3
"""Tulostaa paketin PDF:n korostusvärin ja alueen LaTeX-määrittelyinä.

Käyttö:  python3 yhteiset/korostus.py <paketti>

Väri on paketin taitopuun alueen väri taitopuukartalla, joten PDF ja
kartta tunnistaa samaksi kokonaisuudeksi. Tuntematon paketti saa
oletusvärin.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

# Samat sävyt kuin sivusto/kartta.css:n alueväreissä (tumma muunnelma,
# jotta valkoinen teksti erottuu kansilehdellä).
VARIT = ["2F5F9A", "9A6524", "3E7F3C", "6D4FA0", "B04848", "1F7F77",
         "8A7615", "546676", "4552B0", "A14B7C", "5B7A14", "A4501C",
         "1D6F80", "8C2F8C"]
OLETUS = ("0D7A6C", "Tutoriaalit")


def korostus(paketti: str) -> tuple[str, str]:
    toml = Path(__file__).resolve().parent.parent / "opintopolut" / \
        "taitopuu.toml"
    puu = tomllib.loads(toml.read_text("utf-8"))
    alueet = [a["id"] for a in puu["alue"]]
    nimet = {a["id"]: a["nimi"] for a in puu["alue"]}
    if paketti == "opintopolut":
        return OLETUS[0], "Taitopuu ja opintopolut"
    for t in puu["taito"]:
        if t.get("tutoriaali") == paketti or t["id"] == paketti:
            i = alueet.index(t["alue"])
            return VARIT[i % len(VARIT)], nimet[t["alue"]]
    return OLETUS


def main() -> int:
    vari, alue = korostus(sys.argv[1]) if len(sys.argv) > 1 else OLETUS
    # Alueen nimi ladotaan versaalein. Ääkköset kirjoitetaan XeTeXin
    # ^^^^-merkintänä, koska pandoc voi tulkita komentoriviargumentin
    # väärällä merkistöllä, jos ympäristön lokaali ei ole UTF-8.
    nimi = "".join(c if ord(c) < 128 else f"^^^^{ord(c):04x}"
                   for c in alue.upper())
    print(f"\\def\\korostusvari{{{vari}}}\\def\\aluenimi{{{nimi}}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

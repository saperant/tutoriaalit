#!/usr/bin/env python3
"""Muutoslokin (CHANGELOG.md) rakenteen tarkistin.

Käyttö:  python3 tyokalut/muutosloki.py CHANGELOG.md pyproject.toml

Tarkistaa Keep a Changelog -rakenteen: ylimpänä on osio
``[Julkaisematon]``, versiot ovat semanttisia ja laskevassa
järjestyksessä, päivämäärät ovat ISO 8601 -muodossa ja muutokset on
ryhmitelty sovituilla otsikoilla. Uusimman version on oltava sama kuin
paketin versio.
"""

from __future__ import annotations

import re
import sys
import tomllib
from datetime import date
from pathlib import Path

VERSIO = re.compile(r"^## \[(\d+)\.(\d+)\.(\d+)\] - (\d{4}-\d{2}-\d{2})$")
RYHMAT = {"Lisätty", "Muutettu", "Vanhentunut", "Poistettu", "Korjattu",
          "Tietoturva"}


def tarkista(loki: Path, projekti: Path) -> list[str]:
    """Palauttaa muutoslokin virheet."""
    virheet = []
    otsikot = [(nro, rivi) for nro, rivi
               in enumerate(loki.read_text("utf-8").splitlines(), 1)
               if rivi.startswith("## ") or rivi.startswith("### ")]
    kakkoset = [(n, r) for n, r in otsikot if r.startswith("## ")]
    if not kakkoset or kakkoset[0][1] != "## [Julkaisematon]":
        virheet.append(f"{loki}: ensimmäisen osion on oltava "
                       "[Julkaisematon]")
    versiot: list[tuple[tuple[int, int, int], date]] = []
    for nro, rivi in kakkoset[1:]:
        osuma = VERSIO.match(rivi)
        if not osuma:
            virheet.append(f"{loki}:{nro}: otsikon muoto on "
                           "'## [X.Y.Z] - VVVV-KK-PP'")
            continue
        versio = (int(osuma[1]), int(osuma[2]), int(osuma[3]))
        paiva = date.fromisoformat(osuma[4])
        if versiot and (versio >= versiot[-1][0] or paiva > versiot[-1][1]):
            virheet.append(f"{loki}:{nro}: versiot eivät ole laskevassa "
                           "järjestyksessä")
        versiot.append((versio, paiva))
    for nro, rivi in otsikot:
        if rivi.startswith("### ") and rivi[4:] not in RYHMAT:
            virheet.append(f"{loki}:{nro}: tuntematon ryhmä '{rivi[4:]}'")
    paketti = tomllib.loads(projekti.read_text("utf-8"))["project"]["version"]
    if versiot and ".".join(map(str, versiot[0][0])) != paketti:
        virheet.append(f"{loki}: uusin versio ei ole paketin versio "
                       f"{paketti}")
    if not virheet:
        print(f"OK: {len(versiot)} versiota, uusin {paketti}")
    return virheet


if __name__ == "__main__":
    virheet = tarkista(Path(sys.argv[1]), Path(sys.argv[2]))
    print("\n".join(virheet), end="\n" if virheet else "")
    sys.exit(1 if virheet else 0)

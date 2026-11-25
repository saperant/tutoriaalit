"""Kestojen jäsennys ja muotoilu: "1h30m" on 5400 sekuntia.

Käyttö:  python3 kesto.py KESTO...   (tulostaa kestojen summan)
"""

from __future__ import annotations

import re
import sys

YKSIKOT = {"d": 86400, "h": 3600, "m": 60, "s": 1}
OSA = re.compile(r"(\d+)([dhms])")


# @alku jasenna
def jasenna(teksti: str) -> int:
    """Muuntaa keston sekunneiksi. Yksiköt suurimmasta pienimpään,
    kukin enintään kerran: "2d", "1h30m", "45s"."""
    osat = OSA.findall(teksti)
    if not osat or "".join(a + y for a, y in osat) != teksti:
        raise ValueError(f"ei ole kesto: {teksti!r}")
    yksikot = [y for _, y in osat]
    jarjestys = [y for y in YKSIKOT if y in yksikot]
    if yksikot != jarjestys:
        raise ValueError(f"yksiköt väärässä järjestyksessä: {teksti!r}")
    return sum(int(a) * YKSIKOT[y] for a, y in osat)
# @loppu jasenna


def muotoile(sekunnit: int) -> str:
    """Muotoilee sekunnit lyhimpään muotoon: 5400 on "1h30m"."""
    if sekunnit < 0:
        raise ValueError("kesto ei voi olla negatiivinen")
    osat = []
    for yksikko, pituus in YKSIKOT.items():
        maara, sekunnit = divmod(sekunnit, pituus)
        if maara:
            osat.append(f"{maara}{yksikko}")
    return "".join(osat) or "0s"


def main(argumentit: list[str]) -> int:
    if not argumentit:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        print(muotoile(sum(jasenna(a) for a in argumentit)))
    except ValueError as virhe:
        print(f"virhe: {virhe}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

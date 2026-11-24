"""Komentorivikäyttöliittymä. Logiikka on funktioissa, joita voi
testata ilman aliprosessia; main() vain jäsentää ja tulostaa."""

import argparse
import sys
from collections import Counter
from collections.abc import Iterable, Sequence
from importlib import metadata
from pathlib import Path

from lokikoonti import __version__

TASOT = ("INFO", "WARNING", "ERROR", "FATAL")


# @alku versio
def versio() -> str:
    """Asennetun paketin versio; kehityshakemistosta ajettaessa
    paketin oma vakio."""
    try:
        return metadata.version("lokikoonti")
    except metadata.PackageNotFoundError:
        return __version__
# @loppu versio


# @alku komento
def laske(rivit: Iterable[str]) -> Counter[str]:
    tasot: Counter[str] = Counter()
    for rivi in rivit:
        osat = rivi.split(maxsplit=4)
        if len(osat) >= 4 and osat[0] == "@" and osat[3] in TASOT:
            tasot[osat[3]] += 1
    return tasot


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="lokikoonti")
    p.add_argument("--version", action="version",
                   version=f"%(prog)s {versio()}")
    p.add_argument("tiedostot", nargs="+", type=Path)
    args = p.parse_args(argv)
    yhteensa: Counter[str] = Counter()
    for polku in args.tiedostot:
        with polku.open(encoding="utf-8") as f:
            yhteensa += laske(f)
    for taso in TASOT:
        print(f"{taso:<8}{yhteensa[taso]:>5}")
    return 1 if yhteensa["ERROR"] or yhteensa["FATAL"] else 0
# @loppu komento


if __name__ == "__main__":
    sys.exit(main())

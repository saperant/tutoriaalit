"""Tarkistaa ELF-ohjelman suojaukset readelfin tulosteesta, samaan tapaan
kuin checksec-työkalu.

Käyttö:  python3 tarkista.py OHJELMA...
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass


def readelf(*valitsimet: str) -> str:
    tulos = subprocess.run(["readelf", "-W", *valitsimet], check=True,
                           capture_output=True, text=True)
    return tulos.stdout


# @alku suojaukset
@dataclass
class Suojaukset:
    pie: bool
    nx: bool
    kanari: bool
    relro: str
    fortify: bool
    cet: bool


def tutki(ohjelma: str) -> Suojaukset:
    otsake = readelf("-h", ohjelma)
    segmentit = readelf("-l", ohjelma)
    dynaaminen = readelf("-d", ohjelma)
    symbolit = readelf("--dyn-syms", ohjelma)
    huomautukset = readelf("-n", ohjelma)
    pino = next(r for r in segmentit.splitlines() if "GNU_STACK" in r)
    if "GNU_RELRO" not in segmentit:
        relro = "ei"
    elif "BIND_NOW" in dynaaminen or "Flags: NOW" in dynaaminen:
        relro = "täysi"
    else:
        relro = "osittainen"
    return Suojaukset(
        pie="DYN (" in otsake,
        nx="RWE" not in pino,
        kanari="__stack_chk_fail" in symbolit,
        relro=relro,
        fortify="_chk@" in symbolit,
        cet="IBT, SHSTK" in huomautukset,
    )
# @loppu suojaukset


def main() -> int:
    print(f"{'ohjelma':<10}{'PIE':<7}{'NX':<7}{'kanari':<8}"
          f"{'RELRO':<12}{'FORTIFY':<9}CET")
    for ohjelma in sys.argv[1:]:
        s = tutki(ohjelma)
        kylla = {True: "kyllä", False: "ei"}
        print(f"{ohjelma:<10}{kylla[s.pie]:<7}{kylla[s.nx]:<7}"
              f"{kylla[s.kanari]:<8}{s.relro:<12}{kylla[s.fortify]:<9}"
              f"{kylla[s.cet]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

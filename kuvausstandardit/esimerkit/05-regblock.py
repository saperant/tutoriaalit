"""PeakRDL-regblockin tuottamat rekisterilohkot Verilatorilla.

Ensin tuotettu koodi lint-tarkistetaan ilman poikkeuksia ja sitten
poikkeustiedoston (tb/tuotettu.vlt) kanssa. Lopuksi molemmat
testipenkit käännetään ja ajetaan. Käännöstuotteet menevät
väliaikaiseen hakemistoon.
"""

from __future__ import annotations

import re
import tempfile
from collections import Counter
from pathlib import Path

from kuvaus.ajo import aja
from kuvaus.kaanna import TUOTETUT

TB = Path(__file__).resolve().parent / "tb"


def lahteet(lohko: str) -> list[str]:
    return [str(TUOTETUT / f"{lohko}_pkg.sv"), str(TUOTETUT / f"{lohko}.sv")]


# @alku lint
def lint(lohko: str, poikkeukset: bool) -> Counter[str]:
    """Varoitusten määrät säännöittäin."""
    vlt = [str(TB / "tuotettu.vlt")] if poikkeukset else []
    tulos = aja(["verilator", "--lint-only", "-Wall", *vlt,
                 *lahteet(lohko)], sallittu_virhe=True)
    return Counter(re.findall(r"%Warning-([A-Z]+):", tulos.stderr))
# @loppu lint


# @alku simuloi
def simuloi(lohko: str, tmp: Path) -> list[str]:
    aja(["verilator", "--binary", "--timing", "-Wall", f"-I{TB}",
         "--top-module", f"{lohko}_tb", "-Mdir", str(tmp / lohko),
         "-o", "sim", str(TB / "tuotettu.vlt"), *lahteet(lohko),
         str(TB / f"{lohko}_tb.sv")])
    tulos = aja([str(tmp / lohko / "sim")])
    return [r for r in tulos.stdout.splitlines() if "$finish" not in r]
# @loppu simuloi


def main() -> None:
    for lohko in ("ajastin", "tapahtumat"):
        ilman = lint(lohko, poikkeukset=False)
        kanssa = lint(lohko, poikkeukset=True)
        print(f"{lohko}: varoituksia ilman poikkeuksia "
              f"{sum(ilman.values())}, poikkeusten kanssa "
              f"{sum(kanssa.values())}")
        for saanto, maara in sorted(ilman.items()):
            print(f"  {saanto}: {maara}")
    with tempfile.TemporaryDirectory() as tmp:
        for lohko in ("ajastin", "tapahtumat"):
            print(f"\n{lohko}_tb:")
            for rivi in simuloi(lohko, Path(tmp)):
                print(f"  {rivi}")


if __name__ == "__main__":
    main()

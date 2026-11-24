"""Tuotettujen tiedostojen tahdin tarkistus (CI:n tapaan).

Tallennetut tiedostot verrataan siihen, mitä kuvauksesta nyt
tuotettaisiin. Kaksi tavallista virhettä jää kiinni: tuotettua
tiedostoa on muokattu käsin, tai kuvausta on muutettu mutta tuotettuja
tiedostoja ei ole päivitetty.

    python3 11-tahdissa.py             tarkistaa
    python3 11-tahdissa.py --kirjoita  tuottaa hakemiston tuotettu/
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

from kuvaus.kaanna import RDL, TUOTETUT
from kuvaus.tuota import kirjoita, vertaa


def tila(poikkeavat: list[str]) -> str:
    if not poikkeavat:
        return "ajan tasalla"
    return "VANHENTUNUT: " + ", ".join(poikkeavat)


def main() -> None:
    jasennin = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    jasennin.add_argument("--kirjoita", action="store_true")
    if jasennin.parse_args().kirjoita:
        kirjoita()
    print(f"tuotettu/: {tila(vertaa())}")
    with tempfile.TemporaryDirectory() as hak:
        tmp = Path(hak)
        # @alku kasin
        kopio = tmp / "tuotettu"
        shutil.copytree(TUOTETUT, kopio)
        otsake = kopio / "ajastin.h"
        otsake.write_text(otsake.read_text().replace(
            "JAKAJA_bm 0xff00", "JAKAJA_bm 0x7f00"))
        print(f"kasin muokattu otsake: {tila(vertaa(kopio))}")
        # @loppu kasin
        # @alku kuvaus
        rdl = tmp / "rdl"
        shutil.copytree(RDL, rdl)
        kuvaus = rdl / "ajastin.rdl"
        kuvaus.write_text(kuvaus.read_text().replace(
            "JAKAJA[15:8] = 1;", "JAKAJA[15:8] = 2;"))
        poikkeavat = vertaa(TUOTETUT, rdl)
        print("muutettu kuvaus, tiedostot paivittamatta:")
        for nimi in poikkeavat:
            print(f"  {nimi}")
        # @loppu kuvaus


if __name__ == "__main__":
    main()

"""Tuotettu C-otsake ajurissa ja PeakRDL:n oma otsaketesti.

Ajuri käännetään kahdella kääntäjällä varoitukset virheinä. PeakRDL
tuottaa pyynnöstä (--testcase) myös testiohjelman, joka tarkistaa
rakenteen kenttien siirtymät kuvausta vastaan.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from kuvaus.ajo import aja
from kuvaus.kaanna import RDL, TUOTETUT

JUURI = Path(__file__).resolve().parent
LIPUT = ["-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic"]


def kaantajat() -> list[str]:
    return [k for k in ("gcc-14", "clang-20", "cc") if shutil.which(k)][:2]


def main() -> None:
    with tempfile.TemporaryDirectory() as hak:
        tmp = Path(hak)
        # @alku ajuri
        for kaantaja in kaantajat():
            aja([kaantaja, *LIPUT, f"-I{TUOTETUT}", "-o",
                 str(tmp / "ajuri"), str(JUURI / "c" / "ajuri.c")])
            print(f"c/ajuri.c ({kaantaja}): kaannos onnistui")
        print(aja([str(tmp / "ajuri")]).stdout.rstrip())
        # @loppu ajuri
        # @alku testcase
        aja(["peakrdl", "c-header", str(RDL / "ajastin.rdl"), "-o",
             str(tmp / "ajastin.h"), "--type-style", "hier", "--testcase"])
        testi = tmp / "ajastin.h.test.c"
        tarkistuksia = testi.read_text("utf-8").count("assert(offsetof")
        aja([kaantajat()[0], *LIPUT, f"-I{tmp}", "-o", str(tmp / "testi"),
             str(testi)])
        aja([str(tmp / "testi")])
        print(f"ajastin.h.test.c: {tarkistuksia} siirtymaa tarkistettu")
        # @loppu testcase


if __name__ == "__main__":
    main()

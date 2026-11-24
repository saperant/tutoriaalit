"""Vuon inkrementaalisuus: mitä ajetaan uudelleen ja miksi.

Projekti kopioidaan tilapäishakemistoon, jotta lähteitä voi muuttaa.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from vuo.kooste import markdown
from vuo.kulku import projektin_vuo
from vuo.vaiheet import Vuo

JUURI = Path(__file__).resolve().parent


VAIHEET = ("lint", "synteesi", "sta", "kaannos", "sim")
LYHYET = {"ajettu": "AJETTU", "ajan tasalla": "-", "epäonnistui": "VIRHE",
          "ohitettu": "ohitettu"}
RIVIT: list[list[str]] = []


def nayta(otsikko: str, vuo: Vuo, kohde: str | None = None) -> None:
    """Taulukon rivi: kunkin vaiheen tila tai tyhjä, jos ei kohteena."""
    tilat = vuo.aja(kohde, rinnakkain=2)
    RIVIT.append([otsikko] + [LYHYET.get(tilat.get(v, ""), "")
                              for v in VAIHEET])


# @alku kokeet
def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        projekti = Path(tmp) / "projekti"
        for hak in ("rtl", "tb", "tcl"):
            shutil.copytree(JUURI / hak, projekti / hak)
        vuo = projektin_vuo(projekti, Path(tmp) / "ajo")
        laskuri = projekti / "rtl" / "laskuri.sv"
        alu = projekti / "rtl" / "alu.sv"

        nayta("1. ensimmäinen ajo", vuo)
        nayta("2. ei muutoksia", vuo)
        os.utime(laskuri)                   # sama kuin touch
        nayta("3. touch laskuri.sv", vuo)
        alu.write_text(alu.read_text() + "// kommentti\n")
        nayta("4. kommentti alu.sv", vuo)
        nayta("5. vain kohde sta", vuo, "sta")
        laskuri.write_text(laskuri.read_text().replace("end else", "else"))
        nayta("6. virhe laskuri.sv", vuo)
    print(markdown(("Muutos",) + VAIHEET, RIVIT))
# @loppu kokeet


if __name__ == "__main__":
    main()

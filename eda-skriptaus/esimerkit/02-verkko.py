"""Vuon riippuvuusverkko kuvana: rakenne ja yhden ajon tilat.

Tuloste on Graphvizin DOT-kieltä. Kirjan kuvat piirretään tästä
tulosteesta, joten ne vastaavat vuon kuvausta ja ajon tulosta.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from vuo.kulku import projektin_vuo
from vuo.verkko import dot

JUURI = Path(__file__).resolve().parent


# @alku kuvat
def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        projekti = Path(tmp) / "projekti"
        for hak in ("rtl", "tb", "tcl"):
            shutil.copytree(JUURI / hak, projekti / hak)
        vuo = projektin_vuo(projekti, Path(tmp) / "ajo")
        print(dot(vuo, projekti))

        vuo.aja(rinnakkain=2)
        alu = projekti / "rtl" / "alu.sv"
        alu.write_text(alu.read_text() + "// kommentti\n")
        tilat = vuo.aja(rinnakkain=2)
        print(dot(vuo, projekti, "katkaisu", tilat))
# @loppu kuvat


if __name__ == "__main__":
    main()

"""Muut kuvaukset: ajoitusrajoitteet (SDC) ja virranhallinta (UPF).

Molemmat ovat Tcl-kieltä. Ilman synteesityökalua niistä voi silti
tarkistaa syntaksin ja komentojen nimet ajamalla ne Tcl-tulkissa, jossa
tunnetut komennot on korvattu tulostavilla proseduureilla
(muut/tarkista.tcl). Kirjoitusvirhe komennon nimessä jää kiinni.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from kuvaus.ajo import aja

MUUT = Path(__file__).resolve().parent / "muut"


def tclsh() -> str:
    return next(t for t in ("tclsh8.6", "tclsh") if shutil.which(t))


def main() -> None:
    tarkistin = str(MUUT / "tarkista.tcl")
    tulos = aja([tclsh(), tarkistin, str(MUUT / "ajastin.sdc"),
                 str(MUUT / "ajastin.upf")])
    print(tulos.stdout.rstrip())
    # @alku kirjoitusvirhe
    with tempfile.TemporaryDirectory() as tmp:
        rikki = Path(tmp) / "rikki.sdc"
        rikki.write_text((MUUT / "ajastin.sdc").read_text().replace(
            "set_false_path", "set_flase_path"))
        tulos = aja([tclsh(), tarkistin, str(rikki)], sallittu_virhe=True)
        print(tulos.stdout.rstrip())
        print(f"  paluuarvo {tulos.returncode}")
    # @loppu kirjoitusvirhe


if __name__ == "__main__":
    main()

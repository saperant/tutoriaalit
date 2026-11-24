"""Työkalujen tarkistus ennen vuota ja vuon vaiheet tasoittain."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

from vuo.kulku import projektin_vuo

JUURI = Path(__file__).resolve().parent

# @alku tyokalut
TYOKALUT = [
    ("verilator", "lint ja simulointi"),
    ("iverilog", "toinen simulaattori"),
    ("yosys", "logiikkasynteesi"),
    ("tclsh8.6", "opetus-sta-työkalun tulkki"),
    ("python3", "vuo, jäsentimet ja koosteet"),
]


def tarkista_tyokalut() -> list[str]:
    """Tulostaa työkalut ja palauttaa puuttuvat."""
    puuttuu = []
    for ohjelma, tehtava in TYOKALUT:
        loytyi = shutil.which(ohjelma) is not None
        print(f"{ohjelma:10} {tehtava:28} {'kyllä' if loytyi else 'EI'}")
        if not loytyi:
            puuttuu.append(ohjelma)
    return puuttuu
# @loppu tyokalut


def main() -> int:
    puuttuu = tarkista_tyokalut()
    if puuttuu:
        print(f"Puuttuu: {', '.join(puuttuu)}")
        return 1
    print("Kaikki työkalut löytyvät.")
    # @alku tasot
    with tempfile.TemporaryDirectory() as tmp:
        vuo = projektin_vuo(JUURI, Path(tmp))
        for i, taso in enumerate(vuo.tasot(), 1):
            print(f"taso {i}: {', '.join(taso)}")
    # @loppu tasot
    return 0


if __name__ == "__main__":
    sys.exit(main())

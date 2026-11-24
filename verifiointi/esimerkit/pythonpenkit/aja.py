"""Ajaa cocotb-testimodulin Icarus Verilogilla ja tulostaa tuloksen
tiiviisti ja toistettavasti.

Käyttö: python3 pythonpenkit/aja.py --top fifo --moduuli test_fifo \\
            --lahde rtl/fifo.sv [--vika BUGI_TYHJA] [--siemen 1]
            [--testit satunnaistettu,kulmat]

Simulaattorin oma loki menee rakennushakemistoon. Tulosteeseen tulevat
testien raporttirivit ja yhteenveto. Paluuarvo on 1, jos jokin testi
epäonnistui.
"""

from __future__ import annotations

import argparse
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from cocotb_tools.runner import get_runner

PENKIT = Path(__file__).resolve().parent
ESIMERKIT = PENKIT.parent


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--top", required=True)
    p.add_argument("--moduuli", required=True)
    p.add_argument("--lahde", action="append", required=True)
    p.add_argument("--vika", default="")
    p.add_argument("--siemen", default="1")
    p.add_argument("--testit", default="")
    p.add_argument("--rakennus", default="cocotb", help="alihakemisto")
    a = p.parse_args()

    tunnus = f"{a.moduuli}-{a.vika or 'ehja'}-{a.siemen}-{a.testit}"
    rakennus = ESIMERKIT / "rakennus" / a.rakennus / tunnus
    rakennus.mkdir(parents=True, exist_ok=True)
    raportti = rakennus / "raportti.txt"
    raportti.unlink(missing_ok=True)

    # @alku ajaja
    simulaattori = get_runner("icarus")
    simulaattori.build(
        sources=[ESIMERKIT / f for f in a.lahde],
        hdl_toplevel=a.top,
        build_dir=rakennus,
        always=True,
        defines={a.vika: 1} if a.vika else {},
        timescale=("1ns", "1ps"),
        log_file=rakennus / "kaannos.loki",
    )
    tulokset = simulaattori.test(
        test_module=a.moduuli,
        hdl_toplevel=a.top,
        build_dir=rakennus,
        test_dir=PENKIT,
        testcase=a.testit.split(",") if a.testit else None,
        extra_env={
            "RAPORTTI": str(raportti),
            "SIEMEN": a.siemen,
            "PYTHONPATH": str(PENKIT)
            + os.pathsep
            + os.environ.get("PYTHONPATH", ""),
        },
        results_xml=str(rakennus / "tulokset.xml"),
        log_file=rakennus / "ajo.loki",
    )
    # @loppu ajaja

    if raportti.exists():
        print(raportti.read_text("utf-8"), end="")
    lapi, kaatui = [], []
    for tapaus in ET.parse(tulokset).iter("testcase"):
        virhe = tapaus.find("failure")
        if virhe is None:
            virhe = tapaus.find("error")
        if virhe is None:
            lapi.append(tapaus.get("name", "?"))
        else:
            viesti = (virhe.get("message") or "").splitlines()
            kaatui.append(
                f"{tapaus.get('name')}: {viesti[0] if viesti else 'virhe'}"
            )
    print(f"läpi {len(lapi)}, kaatui {len(kaatui)}")
    for k in kaatui:
        print(f"  KAATUI {k}")
    return 1 if kaatui else 0


if __name__ == "__main__":
    sys.exit(main())

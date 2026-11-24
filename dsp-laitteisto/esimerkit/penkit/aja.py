"""Ajaa cocotb-testimodulin Icarus Verilogilla ja tulostaa tuloksen
tiiviisti ja toistettavasti.

Käyttö: python3 penkit/aja.py --top fir_suora --moduuli test_suodin
            --lahde rtl/fir_suora.sv --lahde rtl/kavenna.sv
            [--vika BUGI_KATKAISU] [--asetus SUODIN=fir] [--siemen 1]

--asetus välittää testimodulille ympäristömuuttujan (esimerkiksi
mikä malli on referenssinä). Simulaattorin oma loki menee
rakennushakemistoon; tulosteeseen tulevat testien raporttirivit ja
yhteenveto. Paluuarvo on 1, jos jokin testi epäonnistui.
"""

from __future__ import annotations

import argparse
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
    p.add_argument("--asetus", action="append", default=[])
    p.add_argument("--siemen", default="1")
    a = p.parse_args()

    asetukset = dict(s.split("=", 1) for s in a.asetus)
    tunnus = "-".join(
        [a.top, a.moduuli, a.vika or "ehja", *asetukset.values()]
    )
    rakennus = ESIMERKIT / "rakennus" / "cocotb" / tunnus
    rakennus.mkdir(parents=True, exist_ok=True)
    raportti = rakennus / "raportti.txt"
    raportti.unlink(missing_ok=True)

    # Ajaja antaa simulaattorille oman sys.path-listansa: testimoduuli
    # tuo mallit paketista malli (esimerkkihakemisto).
    sys.path.insert(0, str(ESIMERKIT))

    # @alku ajaja
    simulaattori = get_runner("icarus")
    simulaattori.build(
        sources=[ESIMERKIT / f for f in a.lahde],
        includes=[ESIMERKIT / "rtl"],
        hdl_toplevel=a.top,
        build_dir=rakennus,
        always=True,
        defines={a.vika: 1} if a.vika else {},
        # Simulaattori ajetaan rakennushakemistossa: taulukot
        # absoluuttisella polulla.
        parameters={"TAULUKKO": f'"{ESIMERKIT / "rtl/nco_sini.hex"}"'}
        if a.top == "nco"
        else {},
        timescale=("1ns", "1ps"),
        log_file=rakennus / "kaannos.loki",
    )
    tulokset = simulaattori.test(
        test_module=a.moduuli,
        hdl_toplevel=a.top,
        build_dir=rakennus,
        test_dir=PENKIT,
        extra_env={
            **asetukset,
            "RAPORTTI": str(raportti),
            "SIEMEN": a.siemen,
        },
        results_xml=str(rakennus / "tulokset.xml"),
        log_file=rakennus / "ajo.loki",
    )
    # @loppu ajaja

    if raportti.exists():
        print(raportti.read_text("utf-8"), end="")
    lapi, kaatui = [], []
    for tapaus in ET.parse(tulokset).iter("testcase"):
        if tapaus.find("skipped") is not None:
            continue  # testi ei koske tätä DUT:ia
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

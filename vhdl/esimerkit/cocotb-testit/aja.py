"""Ajaa cocotb-testit GHDL:llä ja tulostaa tuloksen tiiviisti.

Käyttö (hakemistosta esimerkit/):

    python3 cocotb-testit/aja.py --top sarjavastaanotin \\
        --moduuli test_uart_rx --lahde 06-uart-rx/sarjavastaanotin.vhd \\
        [--parametri KELLOJA_BITTIIN=8] [--siemen 1] \\
        [--mutaatio 'VANHA=>UUSI']

Simulaattorin omat lokit menevät rakennushakemistoon. Tulosteeseen
tulevat testien omat raporttirivit ja yhteenveto, joten tuloste on
sama joka ajolla. Paluuarvo on 1, jos jokin testi epäonnistui.

--mutaatio korvaa lähteestä tekstin ennen kääntämistä. Sillä
tarkistetaan, että testit huomaavat tarkoituksella istutetun vian.
"""

from __future__ import annotations

import argparse
import os
import sys
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

from cocotb_tools.runner import get_runner

TESTIT = Path(__file__).resolve().parent
ESIMERKIT = TESTIT.parent


def lahteet(polut: list[str], mutaatio: str, kohde: Path) -> list[Path]:
    """Palauttaa lähteet; mutaatio tehdään kopioon, ei alkuperäiseen."""
    if not mutaatio:
        return [ESIMERKIT / p for p in polut]
    vanha, uusi = mutaatio.split("=>")
    tulos = []
    for p in polut:
        teksti = (ESIMERKIT / p).read_text("utf-8")
        if vanha in teksti:
            teksti = teksti.replace(vanha, uusi, 1)
            vanha = "\0"                    # vain ensimmäinen osuma
        kopio = kohde / Path(p).name
        kopio.write_text(teksti, "utf-8")
        tulos.append(kopio)
    if vanha != "\0":
        raise SystemExit(f"mutaatio ei osunut: {mutaatio!r}")
    return tulos


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--top", required=True)
    p.add_argument("--moduuli", required=True)
    p.add_argument("--lahde", action="append", required=True)
    p.add_argument("--parametri", action="append", default=[])
    p.add_argument("--siemen", default="1")
    p.add_argument("--mutaatio", default="")
    a = p.parse_args()

    parametrit = dict(x.split("=", 1) for x in a.parametri)
    # Jokaisella ajolla on oma hakemistonsa, jotta ajot voivat kulkea
    # rinnakkain; mutaatio tunnistetaan tiivisteestä.
    mutaatio = f"m{zlib.crc32(a.mutaatio.encode()):08x}" if a.mutaatio else ""
    tunnus = "-".join([a.moduuli, *a.parametri, a.siemen, mutaatio or "ehja"])
    rakennus = ESIMERKIT / "build" / "cocotb" / tunnus
    rakennus.mkdir(parents=True, exist_ok=True)
    raportti = rakennus / "raportti.txt"
    raportti.unlink(missing_ok=True)

    # @alku ajaja
    # GHDL tallentaa käännetyn kirjaston työhakemistoon, ja ajo
    # tapahtuu testihakemistossa, joten työhakemisto annetaan
    # molemmille. Generic-arvot annetaan vasta ajossa.
    vhdl2008 = ["--std=08", f"--workdir={rakennus}"]
    simulaattori = get_runner("ghdl")
    simulaattori.build(
        sources=lahteet(a.lahde, a.mutaatio, rakennus),
        hdl_toplevel=a.top,
        build_dir=rakennus,
        build_args=vhdl2008,
        always=True,
        log_file=rakennus / "kaannos.loki",
    )
    tulokset = simulaattori.test(
        test_module=a.moduuli,
        hdl_toplevel=a.top,
        build_dir=rakennus,
        test_dir=TESTIT,
        test_args=vhdl2008,
        parameters=parametrit,
        extra_env={
            "RAPORTTI": str(raportti),
            "SIEMEN": a.siemen,
            "PYTHONPATH": str(TESTIT)
            + os.pathsep
            + os.environ.get("PYTHONPATH", ""),
        },
        results_xml=str(rakennus / "tulokset.xml"),
        log_file=rakennus / "ajo.loki",
    )
    # @loppu ajaja

    if raportti.exists():
        print(raportti.read_text("utf-8"), end="")
    kaatui = []
    lapi = 0
    for tapaus in ET.parse(tulokset).iter("testcase"):
        virhe = tapaus.find("failure")
        if virhe is None:
            virhe = tapaus.find("error")
        if virhe is None:
            lapi += 1
        else:
            viesti = (virhe.get("message") or "").splitlines()
            kaatui.append(
                f"{tapaus.get('name')}: {viesti[0] if viesti else 'virhe'}"
            )
    print(f"läpi {lapi}, kaatui {len(kaatui)}")
    for k in kaatui:
        print(f"  KAATUI {k}")
    return 1 if kaatui else 0


if __name__ == "__main__":
    sys.exit(main())

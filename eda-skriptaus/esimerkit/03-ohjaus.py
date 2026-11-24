"""Työkalut eräajona: paluuarvot, lokit, aikakatkaisu ja kaksi
simulaattoria saman rajapinnan takana."""

from __future__ import annotations

import tempfile
from pathlib import Path

from vuo.ajo import AIKAKATKAISU, aja
from vuo.raportit import lue_icarus, lue_kattavuus, lue_simulointi
from vuo.simulaattorit import Icarus, Simulaattori, Verilator

JUURI = Path(__file__).resolve().parent
LAHTEET = [JUURI / "rtl" / "alu.sv", JUURI / "tb" / "alu_tb.sv"]


# @alku paluuarvo
def paluuarvot(tmp: Path) -> None:
    ajo = aja(["yosys", "-q", "-p", "read_verilog -sv puuttuu.sv"],
              tmp / "yosys.log", hakemisto=tmp)
    loki = ajo.loki.read_text()
    print(f"yosys, puuttuva tiedosto: paluuarvo {ajo.paluuarvo}, "
          f"ERROR-rivi lokissa: {'kyllä' if 'ERROR:' in loki else 'ei'}")

    sim = Verilator()
    sim.kaanna(LAHTEET, "alu_tb", ["VIKA"], tmp / "v")
    ajo = sim.aja(tmp / "v", ["+siemen=3", "+maara=12"])
    tulos = lue_simulointi(ajo.loki.read_text(), "alu", 3)
    print(f"simulointi, viallinen ALU: paluuarvo {ajo.paluuarvo}, "
          f"testin tulos {tulos.tila}")

    ajo = sim.aja(tmp / "v", ["+jumita"], aikaraja=1.0)
    katkaistu = "kyllä" if ajo.paluuarvo == AIKAKATKAISU else "ei"
    print(f"simulointi, jumi: paluuarvo {ajo.paluuarvo}, "
          f"aikakatkaisu: {katkaistu}")
# @loppu paluuarvo


# @alku simulaattorit
def vertaa_simulaattoreita(tmp: Path) -> None:
    tulokset = {}
    simulaattorit: list[Simulaattori] = [Verilator(), Icarus()]
    for sim in simulaattorit:
        hak = tmp / sim.nimi
        kaannos = sim.kaanna(LAHTEET, "alu_tb", ["VIKA"], hak)
        ajo = sim.aja(hak, ["+siemen=3", "+maara=12"])
        loki = ajo.loki.read_text()
        tulos = lue_simulointi(loki, "alu", 3)
        tulokset[sim.nimi] = (tulos, lue_kattavuus(loki))
        rajoitukset = [v for v in lue_icarus(kaannos.loki.read_text())
                       if v.koodi == "SORRY"]
        print(f"{sim.nimi:9}: {tulos.tila}, virheitä {tulos.virheita}, "
              f"rajoitusilmoituksia: {'kyllä' if rajoitukset else 'ei'}")
    v, i = tulokset["verilator"], tulokset["icarus"]
    print(f"sama tulos ja kattavuus: {'kyllä' if v == i else 'EI'}")
# @loppu simulaattorit


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        paluuarvot(Path(tmp))
        vertaa_simulaattoreita(Path(tmp))


if __name__ == "__main__":
    main()

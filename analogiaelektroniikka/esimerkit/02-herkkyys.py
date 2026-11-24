"""Toimintapisteen herkkyys transistorin vahvistukselle ja lämpötilalle.

Verrataan kahta biasointia: kiinteä kantavastus ja jännitteenjakaja
emitterivastuksella. Molemmat on mitoitettu samaan kollektorivirtaan.
"""

import re
from pathlib import Path

from spice import simuloi

MALLI = (Path(__file__).resolve().parent / "transistorit.lib").read_text()

# @alku piirit
KIINTEA = """
Vcc vcc 0 DC 12
Rb vcc b 910k
Rc vcc c 4.7k
Q1 c b 0 QV
"""
JAKAJA = """
Vcc vcc 0 DC 12
R1 vcc b 47k
R2 b 0 10k
Rc vcc c 4.7k
Re e 0 1k
Q1 c b e QV
"""
# @loppu piirit


# @alku ajo
def kollektorivirta(piiri: str, bf: float, lampotila: float) -> float:
    """Simuloi piirin, jonka transistorin BF on vaihdettu, lämpötilassa."""
    malli = re.search(r"\.model QNPN NPN\(.*?\)", MALLI, re.S)
    assert malli is not None
    rivi = malli.group(0).replace("QNPN", "QV").replace("BF=200", f"BF={bf}")
    netlist = (f"herkkyys\n{rivi}\n{piiri}\n.options TEMP={lampotila}\n"
               ".control\nop\nprint @q1[ic]\n.endc\n.end\n")
    return simuloi(netlist).arvot["@q1[ic]"]


for nimi, piiri in (("kiinteä kantavastus", KIINTEA),
                    ("jakaja ja emitterivastus", JAKAJA)):
    virrat = [kollektorivirta(piiri, bf, t)
              for bf in (100, 200, 400) for t in (0, 27, 85)]
    pienin, suurin = min(virrat), max(virrat)
    print(f"{nimi}: I_c {pienin * 1e3:.2f} ... {suurin * 1e3:.2f} mA, "
          f"suhde {suurin / pienin:.2f}")
# @loppu ajo

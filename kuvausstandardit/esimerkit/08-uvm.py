"""PeakRDL:n tuottama UVM-rekisterimalli verrattuna kuvaukseen.

UVM-mallia ei voi ajaa Verilator 5.020:lla, joten tämä ohjelma lukee
tuotetun luokkakuvauksen ja tarkistaa, että jokaisen kentän leveys,
sijainti, pääsytapa ja nollausarvo vastaavat kuvausta.
"""

from __future__ import annotations

import re

from kuvaus.kaanna import TUOTETUT, kaanna
from kuvaus.malli import rekisterit

# @alku configure
# this.VALMIS.configure(this, 1, 0, "W1C", 1, 'h0, 1, 1, 0);
#   parent, size, lsb_pos, access, volatile, reset, has_reset,
#   is_rand, individually_accessible
CONFIGURE = re.compile(
    r"class ajastin__(\w+) extends uvm_reg|"
    r"this\.(\w+)\.configure\(this, (\d+), (\d+), \"(\w+)\", (\d), "
    r"'h([0-9a-f]+), (\d)")
# @loppu configure


def main() -> None:
    teksti = (TUOTETUT / "ajastin_uvm.sv").read_text("utf-8")
    uvm = {}
    rekisteri = ""
    print(f"{'kentta':<16}{'koko':<6}{'lsb':<5}{'access':<8}"
          f"{'volatile':<10}reset")
    for osuma in CONFIGURE.finditer(teksti):
        if osuma.group(1):
            rekisteri = osuma.group(1)
            continue
        nimi, koko, lsb, access, volatile, reset, has_reset = \
            osuma.groups()[1:]
        polku = f"{rekisteri}.{nimi}"
        nollaus = int(reset, 16) if has_reset == "1" else None
        uvm[polku] = (int(lsb), int(lsb) + int(koko) - 1, access, nollaus)
        print(f"{polku:<16}{koko:<6}{lsb:<5}{access:<8}{volatile:<10}"
              f"{'-' if nollaus is None else hex(nollaus)}")
    # @alku vertaa
    malli = {f"{r.polku}.{k.nimi}": (k.lsb, k.msb, k.paasy, k.nollaus)
             for r in rekisterit(kaanna("ajastin.rdl")) for k in r.kentat}
    erot = sorted(p for p in malli if malli[p] != uvm.get(p))
    print(f"UVM-malli ja kuvaus: {len(malli)} kenttaa, "
          + ("samat" if not erot else "EROAVAT: " + ", ".join(erot)))
    # @loppu vertaa


if __name__ == "__main__":
    main()

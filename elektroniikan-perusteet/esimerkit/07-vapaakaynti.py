"""Vapaakäyntidiodi: induktiivisen kuorman katkaisun jännitepiikki."""

import math

from spice import HAKEMISTO, lopeta, muotoile, simuloi, vertaa

piiri = (HAKEMISTO / "07-vapaakaynti.cir").read_text("utf-8")
# @alku ilman
# Ilman diodia käämin virta siirtyy käämin omaan kapasitanssiin, ja
# energia 1/2 L I^2 muuttuu energiaksi 1/2 C U^2:
L, C, virta = 100e-3, 100e-12, 12.0 / 100
piikki = virta * math.sqrt(L / C)
ilman = simuloi(piiri.replace("D1 d vcc DPIEN", "* ei diodia"))
print(f"ilman diodia: piikki {muotoile(ilman.arvot['huippu'], 'V')}, "
      f"arvio {muotoile(piikki, 'V')}")
# @loppu ilman
# @alku kanssa
kanssa = simuloi(piiri)
vertaa("huippu", kanssa.arvot["huippu"], 12.0 + 0.8, "V", 0.05)
# Diodin kanssa virta vaimenee aikavakiolla L / R: rele päästää hitaammin.
print(f"  virta laskee 37 %:iin {1e3 * (kanssa.arvot['ilaskee'] - 5e-3):.2f}"
      f" ms:ssa (L / R = {1e3 * L / 100:.1f} ms)")
# @loppu kanssa
lopeta()

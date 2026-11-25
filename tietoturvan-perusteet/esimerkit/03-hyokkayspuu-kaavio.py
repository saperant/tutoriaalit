"""Hyökkäyspuu DOT-muodossa: halvin reitti korostettuna."""

import runpy
import textwrap
from pathlib import Path
from typing import Any

# Puu ja laskenta luetaan viereisestä esimerkistä.
malli = runpy.run_path(str(Path(__file__).with_name("03-hyokkayspuu.py")))
puu, halvin = malli["puu"], malli["halvin"]

halvimmat = set(halvin(puu)[1])
laskuri = iter(range(1000))


# @alku piirto
def piirra(s: Any) -> tuple[str, bool]:
    """Tulostaa solmun lapsineen. Palauttaa tunnuksen ja tiedon siitä,
    kuuluuko solmu halvimpaan reittiin."""
    tunnus = f"s{next(laskuri)}"
    nimi = "\\n".join(textwrap.wrap(s.nimi, 20, break_on_hyphens=False))
    if s.tyyppi == "lehti":
        mukana = s.nimi in halvimmat
        paksu = ", penwidth=2.2" if mukana else ""
        print(f'  {tunnus} [label="{nimi}\\n{s.hinta:.0f} €"{paksu}];')
        return tunnus, mukana
    lapset = [piirra(lapsi) for lapsi in s.lapset]
    # TAI-solmussa riittää yksi halvimman reitin lapsi, JA-solmussa
    # tarvitaan kaikki.
    mukana = (any if s.tyyppi == "TAI" else all)(m for _, m in lapset)
    paksu = ", penwidth=2.2" if mukana else ""
    print(f'  {tunnus} [label="{nimi}\\n{s.tyyppi}: {halvin(s)[0]:.0f} €"'
          f", shape=box{paksu}];")
    for lapsi, lapsi_mukana in lapset:
        viiva = " [penwidth=2.2]" if mukana and lapsi_mukana else ""
        print(f"  {tunnus} -> {lapsi}{viiva};")
    return tunnus, mukana
# @loppu piirto


print("digraph {")
print("  nodesep=0.3; ranksep=0.45;")
piirra(puu)
print("}")

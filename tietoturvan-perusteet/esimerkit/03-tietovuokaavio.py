"""Tietovuokaavio DOT-muodossa samasta mallista kuin STRIDE-luettelo."""

import runpy
from pathlib import Path

# Malli luetaan viereisestä esimerkistä, jotta kaavio ja uhkaluettelo
# eivät voi erkaantua toisistaan.
malli = runpy.run_path(str(Path(__file__).with_name("03-stride.py")))
ELEMENTIT, VIRRAT = malli["ELEMENTIT"], malli["VIRRAT"]

# Tietovuokaavion merkintätapa: toimija suorakulmiona, prosessi
# ympyränä ja tietovarasto lieriönä.
MUOTO = {"toimija": "box", "prosessi": "ellipse", "varasto": "cylinder"}

# @alku kaavio
print("digraph {")
print("  nodesep=0.6; ranksep=0.5;")
vyohykkeet = list(dict.fromkeys(e.vyohyke for e in ELEMENTIT))
for i, vyohyke in enumerate(vyohykkeet):
    # Luottamusvyöhyke on katkoviivalla rajattu alue.
    print(f"  subgraph cluster_{i} {{")
    print(f'    label="{vyohyke}"; style=dashed;')
    for j, e in enumerate(ELEMENTIT):
        if e.vyohyke == vyohyke:
            print(f'    e{j} [label="{e.nimi}", shape={MUOTO[e.tyyppi]}];')
    print("  }")
for v in VIRRAT:
    # Rajan ylittävä virta piirretään paksulla viivalla.
    tyyli = ", penwidth=2.2" if v.ylittaa_rajan else ""
    print(f"  e{ELEMENTIT.index(v.mista)} -> e{ELEMENTIT.index(v.mihin)}"
          f' [label="{v.sisalto}"{tyyli}];')
print("}")
# @loppu kaavio

"""Infrastruktuuri koodina pienoiskoossa: suunnitelma ja toteutus.

Käyttö:
  python3 tila.py suunnitelma <haluttu.json> <tila.json>
  python3 tila.py toteuta     <haluttu.json> <tila.json>

Haluttu tila kuvataan tiedostossa (deklaratiivisesti), ja työkalu
laskee, mitä nykyiselle tilalle pitää tehdä. Terraform ja OpenTofu
toimivat samoin: `plan` näyttää erot, `apply` toteuttaa ne ja
päivittää tilatiedoston. Toinen ajo ei muuta mitään (idempotenssi).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

Resurssit = dict[str, dict[str, Any]]


def lue(polku: Path) -> Resurssit:
    if not polku.exists():
        return {}
    tulos: Resurssit = json.loads(polku.read_text("utf-8"))
    return tulos


# @alku suunnitelma
def suunnitelma(haluttu: Resurssit, nykyinen: Resurssit) -> list[str]:
    """Erot haluttuun tilaan: + luonti, ~ muutos, - poisto."""
    rivit = []
    for nimi in sorted(haluttu.keys() | nykyinen.keys()):
        uusi, vanha = haluttu.get(nimi), nykyinen.get(nimi)
        if vanha is None and uusi is not None:
            rivit.append(f"+ {nimi}: luodaan")
            rivit += [f"    {k} = {v}" for k, v in sorted(uusi.items())]
        elif uusi is None or vanha is None:
            rivit.append(f"- {nimi}: poistetaan")
        elif uusi != vanha:
            for avain in sorted(uusi.keys() | vanha.keys()):
                if uusi.get(avain) != vanha.get(avain):
                    rivit.append(f"~ {nimi}.{avain}: "
                                 f"{vanha.get(avain)} -> {uusi.get(avain)}")
    return rivit
# @loppu suunnitelma


def main(argv: list[str]) -> int:
    toiminto, tila_polku = argv[0], Path(argv[2])
    haluttu, nykyinen = lue(Path(argv[1])), lue(tila_polku)
    muutokset = suunnitelma(haluttu, nykyinen)
    for rivi in muutokset:
        print(rivi)
    if not muutokset:
        print("ei muutoksia: infrastruktuuri vastaa kuvausta")
    elif toiminto == "toteuta":
        # Oikea työkalu kutsuisi tässä pilvipalvelun rajapintaa.
        tila_polku.write_text(json.dumps(haluttu, indent=2), "utf-8")
        maara = sum(not r.startswith(" ") for r in muutokset)
        print(f"toteutettu: {maara} muutosta")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

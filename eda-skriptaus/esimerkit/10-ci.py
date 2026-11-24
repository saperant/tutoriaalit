"""CI-putki vuon kuvauksesta: tarkistus ja GitHub Actions -tiedosto.

    python3 10-ci.py             tarkistaa, että ci/laitteisto.yml on
                                 ajan tasalla
    python3 10-ci.py --kirjoita  kirjoittaa sen uudelleen
"""

from __future__ import annotations

import argparse
import tempfile
from dataclasses import replace
from pathlib import Path

from vuo.ci import lue_putki, tarkista, yaml
from vuo.kooste import markdown
from vuo.kulku import projektin_vuo

JUURI = Path(__file__).resolve().parent
YAML = JUURI / "ci" / "laitteisto.yml"


# @alku main
def main() -> None:
    jasennin = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    jasennin.add_argument("--kirjoita", action="store_true")
    argumentit = jasennin.parse_args()
    putki, tyot = lue_putki(JUURI / "asetukset" / "ci.toml")
    with tempfile.TemporaryDirectory() as tmp:
        vuo = projektin_vuo(JUURI, Path(tmp))
        virheet = tarkista(tyot, vuo)
        print(markdown(("Työ", "Ajaa", "Tarvitsee"),
                       [(t.nimi, t.kohde or t.ajo,
                         ", ".join(t.tarvitsee) or "-") for t in tyot]))
        print(f"tarkistus: {len(virheet)} virhettä")
        # Sama putki ilman toteutuksen riippuvuutta lintiin.
        rikki = [replace(t, tarvitsee=()) if t.nimi == "toteutus" else t
                 for t in tyot]
        print("ilman toteutuksen riippuvuutta:")
        for virhe in tarkista(rikki, vuo):
            print(f"  {virhe}")
    teksti = yaml(putki, tyot)
    if argumentit.kirjoita:
        YAML.write_text(teksti, encoding="utf-8")
    ajan_tasalla = YAML.exists() and YAML.read_text() == teksti
    print(f"ci/laitteisto.yml: "
          f"{'ajan tasalla' if ajan_tasalla else 'VANHENTUNUT'}")
# @loppu main


if __name__ == "__main__":
    main()

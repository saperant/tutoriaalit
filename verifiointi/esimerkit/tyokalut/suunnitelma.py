"""Tarkistaa verifiointisuunnitelman viitteet (luku 2).

Suunnitelma on TOML-tiedosto, jossa jokaisella vaatimuksella on
tarkistukset ja kattavuuskohteet. Viite tiedosto#teksti on kunnossa,
kun teksti löytyy tiedostosta. Työkalu raportoi vaatimukset, joilta
puuttuu tarkistus tai kattavuuskohde, ja viitteet, joita ei löydy.

Käyttö: python3 tyokalut/suunnitelma.py suunnitelma/fifo.toml
Paluuarvo on 1, jos jokin viite ei löydy.
"""

import sys
import tomllib
from pathlib import Path

LAJIT = {"tarkistukset": "tarkistus", "kattavuus": "kattavuus"}


# @alku viite
def loytyy(viite: str) -> bool:
    tiedosto, _, teksti = viite.partition("#")
    polku = Path(tiedosto)
    return polku.is_file() and teksti in polku.read_text("utf-8")
    # @loppu viite


def main() -> int:
    suunnitelma = tomllib.loads(Path(sys.argv[1]).read_text("utf-8"))
    vaatimukset = suunnitelma["vaatimus"]
    rikki = aukkoja = 0
    for v in vaatimukset:
        print(f"{v['id']}  {v['kuvaus']}")
        for laji, nimi in LAJIT.items():
            if not v[laji]:
                print(f"    AUKKO: ei kohdetta {nimi}")
                aukkoja += 1
            for viite in v[laji]:
                tila = "ok" if loytyy(viite) else "EI LÖYDY"
                rikki += tila != "ok"
                print(f"    {nimi:<9}  {tila:<8}  {viite}")
    print(
        f"{len(vaatimukset)} vaatimusta, {aukkoja} aukkoa, "
        f"{rikki} rikkinäistä viitettä"
    )
    return 1 if rikki else 0


if __name__ == "__main__":
    sys.exit(main())

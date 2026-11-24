"""Kenttien käyttäytyminen: mitä ohjelmisto ja laitteisto näkevät.

Pääsytapa (RW, RO, W1C, RC ...) kertoo ohjelmiston näkymän. Toiminnot
(hwset, counter, intr, singlepulse, swmod, swacc) kertovat, mitä
signaaleja laitteiston puolelle syntyy.
"""

from __future__ import annotations

from kuvaus.kaanna import TUOTETUT, kaanna
from kuvaus.malli import rekisterit


def main() -> None:
    lohko = kaanna("kayttaytyminen.rdl")
    for rek in rekisterit(lohko):
        for k in rek.kentat:
            print(f"{rek.polku + '.' + k.nimi:<22}{k.paasy:<5}"
                  f"{', '.join(k.toiminnot) or '-'}")
    # @alku hwif
    print("\nlaitteiston liitanta (tapahtumat_hwif.rpt):")
    raportti = (TUOTETUT / "tapahtumat_hwif.rpt").read_text("utf-8")
    for rivi in raportti.splitlines():
        print(f"  {rivi}")
    # @loppu hwif


if __name__ == "__main__":
    main()

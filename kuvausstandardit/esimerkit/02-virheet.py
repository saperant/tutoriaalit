"""Kääntäjän tarkistukset tahallaan virheellisille kuvauksille.

Virheet (error) kerätään ensin kaikki, ja käännös pysähtyy vasta sen
jälkeen. Kohtalokas virhe (fatal), kuten viittaus olemattomaan
rekisteriin, pysäyttää käännöksen heti.
"""

from __future__ import annotations

import textwrap

from kuvaus.kaanna import RDL, KaannosVirhe, kaanna


def main() -> None:
    for polku in sorted((RDL / "virheet").glob("*.rdl")):
        print(f"{polku.name}:")
        try:
            kaanna(polku.relative_to(RDL))
        except KaannosVirhe as virhe:
            for viesti in virhe.viestit:
                tiedosto, _, teksti = viesti.partition(":")
                if tiedosto == polku.name:
                    viesti = f"rivi {teksti.strip()}"
                print(textwrap.fill(viesti, width=76, initial_indent="  ",
                                    subsequent_indent="      "))
        else:
            print("  EI VIRHEITA (odotettiin virheita)")


if __name__ == "__main__":
    main()

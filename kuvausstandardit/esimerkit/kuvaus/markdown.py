"""Rekisteridokumentti Markdownina.

Oma generaattori näyttää, kuinka vähän koodia tarvitaan, kun malli on
valmiiksi tarkistettu: kääntäjä on jo varmistanut, ettei kenttiä ole
päällekkäin ja että nollausarvot mahtuvat kenttiin.
"""

from __future__ import annotations

from systemrdl.node import AddrmapNode

from .malli import Kentta, rekisterit


def bitit(kentta: Kentta) -> str:
    if kentta.leveys == 1:
        return str(kentta.lsb)
    return f"{kentta.msb}:{kentta.lsb}"


def nollaus(kentta: Kentta) -> str:
    return "-" if kentta.nollaus is None else f"0x{kentta.nollaus:X}"


# @alku dokumentti
def dokumentti(ylin: AddrmapNode, lahde: str) -> str:
    rivit = [f"# {ylin.get_property('name')} ({ylin.inst_name})", "",
             f"Tuotettu tiedostosta {lahde}. Ala muokkaa kasin.", ""]
    for rek in rekisterit(ylin):
        otsikko = f"## {rek.polku} (0x{rek.osoite:03X}): {rek.kuvaus}"
        rivit += [otsikko, "",
                  "| Bitit | Kentta | Paasy | Nollaus | Kuvaus |",
                  "|-------|--------|-------|---------|--------|"]
        for k in sorted(rek.kentat, key=lambda k: -k.lsb):
            kuvaus = k.kuvaus
            if k.toiminnot:
                kuvaus += f" ({', '.join(k.toiminnot)})"
            rivit.append(f"| {bitit(k)} | {k.nimi} | {k.paasy} "
                         f"| {nollaus(k)} | {kuvaus.strip()} |")
        rivit.append("")
    return "\n".join(rivit)
# @loppu dokumentti

"""Ajastinlohkon kuvaus käännettynä: rekisterit, kentät ja pääsytavat.

Kääntäjä tarkistaa kuvauksen ja tuottaa mallin, jonka jokainen
generaattori lukee. Tämä ohjelma tulostaa mallin taulukkona.
"""

from __future__ import annotations

from kuvaus.kaanna import kaanna
from kuvaus.malli import rekisterit


# @alku taulukko
def main() -> None:
    ajastin = kaanna("ajastin.rdl")
    print(f"{ajastin.inst_name}: {ajastin.size} tavua, "
          f"{len(rekisterit(ajastin))} rekisteria")
    print(f"{'osoite':<7}{'kentta':<16}{'bitit':<7}{'paasy':<6}"
          f"{'nollaus':<9}toiminnot")
    for rek in rekisterit(ajastin):
        for k in rek.kentat:
            bitit = f"{k.msb}:{k.lsb}"
            nollaus = "-" if k.nollaus is None else f"0x{k.nollaus:X}"
            rivi = (f"0x{rek.osoite:02X}   {rek.polku + '.' + k.nimi:<16}"
                    f"{bitit:<7}{k.paasy:<6}{nollaus:<9}"
                    f"{' '.join(k.toiminnot)}")
            print(rivi.rstrip())
# @loppu taulukko


if __name__ == "__main__":
    main()

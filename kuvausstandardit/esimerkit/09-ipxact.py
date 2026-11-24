"""IP-XACT: vienti, XML:n lukeminen Pythonilla ja tuonti takaisin.

Tallennettu IP-XACT-tiedosto tarkistetaan xmllintillä ja luetaan
ElementTreellä. Sitten se tuodaan takaisin SystemRDL-malliksi, ja
mallia verrataan alkuperäiseen: osoitteet, bitit, pääsytavat ja
nollausarvot säilyvät, mutta osa laitteiston käyttäytymisestä ei.
"""

from __future__ import annotations

import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from peakrdl_ipxact import IPXACTImporter
from systemrdl.compiler import RDLCompiler

from kuvaus.ajo import aja
from kuvaus.kaanna import RDL, TUOTETUT, kaanna
from kuvaus.malli import Rekisteri, rekisterit

# @alku lue
NS = {"ipxact": "http://www.accellera.org/XMLSchema/IPXACT/1685-2014"}


def arvo(teksti: str | None) -> int:
    """IP-XACT 2014 kirjoittaa luvut SystemVerilogin tapaan ('h10)."""
    teksti = (teksti or "0").strip()
    return int(teksti[2:], 16) if teksti.startswith("'h") else int(teksti)


def lue_xml(polku: Path) -> None:
    juuri = ET.parse(polku).getroot()
    nimi = juuri.findtext("ipxact:name", namespaces=NS)
    for lohko in juuri.iterfind(".//ipxact:addressBlock", NS):
        perus = arvo(lohko.findtext("ipxact:baseAddress", namespaces=NS))
        alue = arvo(lohko.findtext("ipxact:range", namespaces=NS))
        print(f"{nimi}: addressBlock {perus:#x}, {alue:#x} tavua")
        for rek in lohko.iterfind("ipxact:register", NS):
            siirtyma = arvo(rek.findtext("ipxact:addressOffset",
                                         namespaces=NS))
            kentat = [k.findtext("ipxact:name", namespaces=NS)
                      for k in rek.iterfind("ipxact:field", NS)]
            print(f"  {siirtyma:#04x} {rek.findtext('ipxact:name',
                                                    namespaces=NS):<8}"
                  f" {', '.join(str(k) for k in kentat)}")
# @loppu lue


# @alku tuonti
def tuo(polku: Path) -> list[Rekisteri]:
    kaantaja = RDLCompiler()
    IPXACTImporter(kaantaja).import_file(str(polku))
    return rekisterit(kaantaja.elaborate().top)


def vertaa(nimi: str, alkuperainen: list[Rekisteri],
           tuotu: list[Rekisteri]) -> None:
    # Tuonti lisää tasoksi addressBlockin nimen (ajastin.CTRL).
    tuodut = {r.polku.split(".", 1)[1]: r for r in tuotu}
    sama, kaikki, menetetty = 0, 0, []
    for rek in alkuperainen:
        vastine = {k.nimi: k for k in tuodut[rek.polku].kentat}
        for k in rek.kentat:
            t = vastine[k.nimi]
            kaikki += 1
            if (k.lsb, k.msb, k.paasy, k.nollaus) == \
                    (t.lsb, t.msb, t.paasy, t.nollaus):
                sama += 1
            if k.toiminnot and not t.toiminnot:
                menetetty.append(f"{rek.polku}.{k.nimi}: "
                                 f"{', '.join(k.toiminnot)}")
    print(f"{nimi}: {sama}/{kaikki} kenttaa samoin bitein, paasyin ja "
          "nollausarvoin")
    for rivi in menetetty:
        print(f"  menetetty {rivi}")
# @loppu tuonti


def main() -> None:
    xml = TUOTETUT / "ajastin.xml"
    aja(["xmllint", "--noout", str(xml)])
    print("ajastin.xml: hyvin muodostettu XML")
    lue_xml(xml)
    print()
    vertaa("ajastin", rekisterit(kaanna("ajastin.rdl")), tuo(xml))
    with tempfile.TemporaryDirectory() as tmp:
        polku = Path(tmp) / "tapahtumat.xml"
        aja(["peakrdl", "ip-xact", str(RDL / "kayttaytyminen.rdl"),
             "-o", str(polku)])
        vertaa("tapahtumat", rekisterit(kaanna("kayttaytyminen.rdl")),
               tuo(polku))


if __name__ == "__main__":
    main()

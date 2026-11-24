"""Ohjelmiston näkymä samasta kuvauksesta: CMSIS-SVD ja laitepuu.

SVD-tiedosto luetaan kuten debuggeri sen lukisi: periytyvät
oheislaitteet (derivedFrom) ja klusteritaulukot (dim) puretaan
osoitteiksi, ja osoitteita verrataan malliin. Laitepuun solmut
käännetään dtc:llä, jotta niiden syntaksi on varmasti oikein.
"""

from __future__ import annotations

import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from kuvaus.ajo import aja
from kuvaus.kaanna import TUOTETUT, kaanna
from kuvaus.malli import rekisterit


def luku(e: ET.Element, tagi: str) -> int:
    return int(e.findtext(tagi) or "0", 0)


# @alku svd
def osoitteet(ryhma: ET.Element, perus: int, etuliite: str) -> list[str]:
    """Rekisterien osoitteet ryhmästä; klusteritaulukko puretaan."""
    tulos = []
    for e in ryhma:
        if e.tag == "register":
            osoite = perus + luku(e, "addressOffset")
            tulos.append(f"{osoite:#x} {etuliite}{e.findtext('name')}")
        elif e.tag == "cluster":
            nimi = e.findtext("name") or ""
            for i in range(luku(e, "dim") or 1):
                alku = perus + luku(e, "addressOffset") \
                    + i * luku(e, "dimIncrement")
                tulos += osoitteet(e, alku,
                                   f"{etuliite}{nimi.replace('%s', str(i))}.")
    return tulos


def lue_svd(polku: Path) -> list[str]:
    laite = ET.parse(polku).getroot()
    oheis = {p.findtext("name"): p for p in laite.iter("peripheral")}
    tulos = []
    for nimi, p in oheis.items():
        malli = oheis.get(p.get("derivedFrom"), p)  # periytyvät rekisterit
        rekisterit_e = malli.find("registers")
        assert rekisterit_e is not None
        tulos += osoitteet(rekisterit_e, luku(p, "baseAddress"),
                           f"{nimi}.")
    return tulos
# @loppu svd


# @alku laitepuu
def laitepuu(tmp: Path) -> None:
    dts = tmp / "piiri.dts"
    dts.write_text('/dts-v1/;\n\n/ {\n    #address-cells = <1>;\n'
                   '    #size-cells = <1>;\n\n    soc {\n'
                   '        #address-cells = <1>;\n'
                   '        #size-cells = <1>;\n'
                   '        ranges;\n\n'
                   '        /include/ "soc.dtsi"\n    };\n};\n')
    (tmp / "soc.dtsi").write_text((TUOTETUT / "soc.dtsi").read_text())
    aja(["dtc", "-I", "dts", "-O", "dtb", "-q", "-o", str(tmp / "piiri.dtb"),
         str(dts)])
    takaisin = aja(["dtc", "-I", "dtb", "-O", "dts", "-q",
                    str(tmp / "piiri.dtb")]).stdout
    print("laitepuu: dtc kaansi solmut; takaisin purettuna:")
    for rivi in takaisin.splitlines():
        if "@" in rivi or "reg =" in rivi or "interrupts" in rivi:
            print(f"  {rivi.strip()}")
# @loppu laitepuu


def main() -> None:
    svd = TUOTETUT / "soc.svd"
    aja(["xmllint", "--noout", str(svd)])
    svd_osoitteet = lue_svd(svd)
    malli = [f"{r.osoite:#x} {r.polku}"
             for r in rekisterit(kaanna("soc.rdl"))]
    print(f"soc.svd: hyvin muodostettu, {len(svd_osoitteet)} rekisteria")
    sama = sorted(svd_osoitteet) == sorted(malli)
    print(f"SVD ja kuvaus: {'samat osoitteet' if sama else 'EROAVAT'}")
    for rivi in svd_osoitteet[8:12]:
        print(f"  {rivi}")
    with tempfile.TemporaryDirectory() as tmp:
        laitepuu(Path(tmp))


if __name__ == "__main__":
    main()

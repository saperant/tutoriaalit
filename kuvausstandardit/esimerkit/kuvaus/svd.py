"""CMSIS-SVD-tiedosto järjestelmäpiirin kuvauksesta.

SVD (System View Description) on Arm CMSIS -standardin XML-muoto, jonka
debuggerit ja koodigeneraattorit lukevat. Jokaisesta ylimmän tason
osoitekartan lapsesta tulee oheislaite (peripheral). Samaa tyyppiä
olevat oheislaitteet viittaavat ensimmäiseen (derivedFrom), ja
rekisteriryhmien taulukoista tulee klustereita (cluster, dim).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from systemrdl.node import (AddrmapNode, FieldNode, Node, RegfileNode,
                            RegNode)

from .malli import kentta as kentta_tietue


# @alku paasy
def svd_paasy(paasy: str) -> tuple[str, dict[str, str]]:
    """UVM-lyhenne SVD:n access-arvoksi ja lisäelementeiksi."""
    lisat: dict[str, str] = {}
    if paasy == "W1C":
        lisat["modifiedWriteValues"] = "oneToClear"
    if paasy == "W1S":
        lisat["modifiedWriteValues"] = "oneToSet"
    if paasy in ("RC", "WRC"):
        lisat["readAction"] = "clear"
    access = {"RO": "read-only", "RC": "read-only", "WO": "write-only",
              "WO1": "writeOnce"}.get(paasy, "read-write")
    return access, lisat
# @loppu paasy


def teksti(ylempi: ET.Element, tagi: str, arvo: str) -> None:
    ET.SubElement(ylempi, tagi).text = arvo


def kentta(ylempi: ET.Element, solmu: FieldNode) -> None:
    k = kentta_tietue(solmu)
    e = ET.SubElement(ylempi, "field")
    teksti(e, "name", k.nimi)
    if k.kuvaus:
        teksti(e, "description", k.kuvaus)
    teksti(e, "bitOffset", str(k.lsb))
    teksti(e, "bitWidth", str(k.leveys))
    access, lisat = svd_paasy(k.paasy)
    teksti(e, "access", access)
    for tagi, arvo in lisat.items():
        teksti(e, tagi, arvo)


def rekisteri(ylempi: ET.Element, solmu: RegNode, siirtyma: int) -> None:
    e = ET.SubElement(ylempi, "register")
    teksti(e, "name", solmu.inst_name)
    teksti(e, "description", solmu.get_property("name"))
    teksti(e, "addressOffset", f"0x{siirtyma:X}")
    teksti(e, "size", str(solmu.size * 8))
    nollaus = 0
    for k in solmu.fields():
        arvo = k.get_property("reset")
        if isinstance(arvo, int):
            nollaus |= arvo << k.lsb
    teksti(e, "resetValue", f"0x{nollaus:08X}")
    kentat = ET.SubElement(e, "fields")
    for k in solmu.fields():
        kentta(kentat, k)


def lapset(ylempi: ET.Element, solmu: Node, perus: int) -> None:
    """Rekisterit ja rekisteriryhmät; taulukko kuvataan kerran (dim)."""
    for lapsi in solmu.children(unroll=False):
        if isinstance(lapsi, RegNode):
            rekisteri(ylempi, lapsi, lapsi.raw_absolute_address - perus)
        elif isinstance(lapsi, RegfileNode):
            siirtyma = lapsi.raw_absolute_address - perus
            c = ET.SubElement(ylempi, "cluster")
            if lapsi.array_dimensions and lapsi.array_stride:
                teksti(c, "dim", str(lapsi.array_dimensions[0]))
                teksti(c, "dimIncrement", f"0x{lapsi.array_stride:X}")
                teksti(c, "name", f"{lapsi.inst_name}[%s]")
            else:
                teksti(c, "name", lapsi.inst_name)
            teksti(c, "addressOffset", f"0x{siirtyma:X}")
            lapsi_perus = lapsi.raw_absolute_address
            lapset(c, lapsi, lapsi_perus)


# @alku oheislaite
def oheislaite(ylempi: ET.Element, solmu: AddrmapNode,
               ensimmaiset: dict[str, str]) -> None:
    e = ET.SubElement(ylempi, "peripheral")
    tyyppi = solmu.orig_type_name or solmu.inst_name
    if tyyppi in ensimmaiset:
        e.set("derivedFrom", ensimmaiset[tyyppi])
    teksti(e, "name", solmu.inst_name)
    if tyyppi not in ensimmaiset:
        teksti(e, "description", solmu.get_property("name"))
    teksti(e, "baseAddress", f"0x{solmu.absolute_address:08X}")
    nro = solmu.get_property("keskeytys")
    if nro is not None:
        k = ET.SubElement(e, "interrupt")
        teksti(k, "name", f"{solmu.inst_name}_IRQ")
        teksti(k, "value", str(nro))
    if tyyppi in ensimmaiset:
        return  # rekisterit periytyvät
    ensimmaiset[tyyppi] = solmu.inst_name
    lohko = ET.SubElement(e, "addressBlock")
    teksti(lohko, "offset", "0x0")
    teksti(lohko, "size", f"0x{solmu.size:X}")
    teksti(lohko, "usage", "registers")
    rekisterit = ET.SubElement(e, "registers")
    lapset(rekisterit, solmu, solmu.raw_absolute_address)
# @loppu oheislaite


def svd(ylin: AddrmapNode) -> str:
    laite = ET.Element("device", {"schemaVersion": "1.3"})
    teksti(laite, "name", ylin.inst_name.upper())
    teksti(laite, "version", "1.0")
    teksti(laite, "description", ylin.get_property("name"))
    teksti(laite, "addressUnitBits", "8")
    teksti(laite, "width", "32")
    teksti(laite, "size", "32")
    teksti(laite, "access", "read-write")
    oheis = ET.SubElement(laite, "peripherals")
    ensimmaiset: dict[str, str] = {}
    for lapsi in ylin.children():
        if isinstance(lapsi, AddrmapNode):
            oheislaite(oheis, lapsi, ensimmaiset)
    ET.indent(laite, space="  ")
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            + ET.tostring(laite, encoding="unicode") + "\n")

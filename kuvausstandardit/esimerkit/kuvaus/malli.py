"""Käännetyn SystemRDL-mallin läpikäynti.

Generaattorit eivät käytä kääntäjän solmuja suoraan vaan näitä pieniä
tietueita. Näin jokainen generaattori näkee rekisterit samassa
muodossa, ja tietueita on helppo verrata keskenään (esimerkiksi
IP-XACT-tiedostosta tuotua mallia alkuperäiseen).
"""

from __future__ import annotations

from dataclasses import dataclass

from systemrdl.node import AddrmapNode, FieldNode, RegNode
from systemrdl.rdltypes.builtin_enums import (AccessType, OnReadType,
                                              OnWriteType)


# @alku tietueet
@dataclass(frozen=True)
class Kentta:
    nimi: str
    lsb: int
    msb: int
    paasy: str              # UVM-tyylinen lyhenne: RW, RO, W1C, RC ...
    nollaus: int | None     # None: ei nollausarvoa (laitteiston arvo)
    toiminnot: tuple[str, ...]  # esim. ("hwset", "intr")
    kuvaus: str

    @property
    def leveys(self) -> int:
        return self.msb - self.lsb + 1

    @property
    def maski(self) -> int:
        return ((1 << self.leveys) - 1) << self.lsb


@dataclass(frozen=True)
class Rekisteri:
    polku: str              # suhteessa ylimpään osoitekarttaan
    osoite: int             # absoluuttinen
    koko: int               # tavuina
    kentat: tuple[Kentta, ...]
    kuvaus: str
    turvallinen: bool       # oma ominaisuus, ks. rdl/ominaisuudet.rdl
# @loppu tietueet


# @alku paasy
def paasy(kentta: FieldNode) -> str:
    """Kentän ohjelmistopääsy UVM:n lyhenteinä (RW, RO, WO, W1C, RC ...).

    Sama sanasto on IP-XACT:ssa ja useimmissa rekisterityökaluissa.
    """
    sw = kentta.get_property("sw")
    onread = kentta.get_property("onread")
    onwrite = kentta.get_property("onwrite")
    if onwrite == OnWriteType.woclr:
        return "W1C"
    if onwrite == OnWriteType.woset:
        return "W1S"
    if onread == OnReadType.rclr:
        return "RC" if sw == AccessType.r else "WRC"
    if onread == OnReadType.rset:
        return "RS"
    return {AccessType.rw: "RW", AccessType.r: "RO",
            AccessType.w: "WO", AccessType.rw1: "W1",
            AccessType.w1: "WO1"}.get(sw, "NA")
# @loppu paasy


TOIMINNOT = ("hwset", "hwclr", "counter", "intr", "singlepulse",
             "swmod", "swacc")


def kentta(solmu: FieldNode) -> Kentta:
    toiminnot = tuple(n for n in TOIMINNOT if solmu.get_property(n))
    nollaus = solmu.get_property("reset")
    return Kentta(
        nimi=solmu.inst_name, lsb=solmu.lsb, msb=solmu.msb,
        paasy=paasy(solmu),
        nollaus=nollaus if isinstance(nollaus, int) else None,
        toiminnot=toiminnot,
        kuvaus=" ".join((solmu.get_property("desc") or "").split()))


# @alku rekisterit
def rekisterit(ylin: AddrmapNode) -> list[Rekisteri]:
    """Kaikki rekisterit osoitejärjestyksessä, taulukot purettuina."""
    tulos = []
    for solmu in ylin.descendants(unroll=True):
        if not isinstance(solmu, RegNode):
            continue
        tulos.append(Rekisteri(
            polku=solmu.get_rel_path(ylin),
            osoite=solmu.absolute_address,
            koko=solmu.size,
            kentat=tuple(kentta(k) for k in solmu.fields()),
            kuvaus=solmu.get_property("name"),
            turvallinen=turvallinen(solmu)))
    return sorted(tulos, key=lambda r: r.osoite)
# @loppu rekisterit


def turvallinen(solmu: RegNode) -> bool:
    """Oma ominaisuus ``turvallinen``; puuttuu kuvauksista, jotka eivät
    sisällytä tiedostoa ominaisuudet.rdl."""
    if "turvallinen" not in solmu.list_properties(include_udp=True):
        return False
    return bool(solmu.get_property("turvallinen"))

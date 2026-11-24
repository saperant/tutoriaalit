"""Varastopalvelu: varaa tuotteen ja laskee tilauksen hinnan."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from varasto.hinnat import Hinta
from varasto.varasto import Varasto


class Hintalahde(Protocol):
    def hae(self, sku: str) -> Hinta: ...


class Tapahtumat(Protocol):
    def varattu(self, tunnus: int, sku: str, maara: int) -> None: ...


@dataclass(frozen=True)
class Tilaus:
    varaus: int
    sku: str
    maara: int
    yhteensa_snt: int


# @alku palvelu
class VarastoPalvelu:
    """Liiketoimintalogiikka riippuvuuksien rajapintojen varassa.

    Yksikkötesti antaa väärennökset, integraatiotesti oikeat
    toteutukset; palvelun koodi ei tiedä eroa."""

    def __init__(self, varasto: Varasto, hinnat: Hintalahde,
                 tapahtumat: Tapahtumat) -> None:
        self.varasto = varasto
        self.hinnat = hinnat
        self.tapahtumat = tapahtumat

    def tilaa(self, sku: str, maara: int) -> Tilaus:
        # Hinta haetaan ennen varausta: jos hintapalvelu ei vastaa,
        # saldoa ei lukita turhaan.
        hinta = self.hinnat.hae(sku)
        varaus = self.varasto.varaa(sku, maara)
        self.tapahtumat.varattu(varaus.tunnus, varaus.sku, maara)
        return Tilaus(varaus.tunnus, varaus.sku, maara,
                      hinta.hinta_snt * maara)
# @loppu palvelu

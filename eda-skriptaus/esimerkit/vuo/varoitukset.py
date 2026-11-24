"""Varoitusten luokittelu ja sallittujen varoitusten lista."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from vuo.malli import Varoitus

# @alku vakavuus
# Koodin vakavuus. Tuntematon koodi on varoitus: uusi työkaluversio voi
# tuoda koodeja, joita lista ei vielä tunne.
VAKAVUUS = {
    "ERROR": "virhe", "LATCH": "virhe", "MULTIDRIVEN": "virhe",
    "WIDTHTRUNC": "varoitus", "WIDTHEXPAND": "varoitus",
    "UNUSEDSIGNAL": "tyyli", "UNUSEDPARAM": "tyyli", "DECLFILENAME": "tyyli",
    "SORRY": "työkalu",
}


def vakavuus(v: Varoitus) -> str:
    return VAKAVUUS.get(v.koodi, "varoitus")
# @loppu vakavuus


# @alku poikkeus
@dataclass(frozen=True)
class Sallittu:
    """Hyväksytty varoitus: mikä, miksi ja kuinka pitkään."""

    koodi: str
    tiedosto: str
    kuvio: str          # säännöllinen lauseke viestille
    peruste: str
    voimassa: date

    # @alku koskee
    def koskee(self, v: Varoitus) -> bool:
        return (v.koodi == self.koodi and v.tiedosto == self.tiedosto
                and re.search(self.kuvio, v.viesti) is not None)
    # @loppu koskee


def lue_sallitut(polku: Path) -> list[Sallittu]:
    data = tomllib.loads(polku.read_text(encoding="utf-8"))
    tulos = []
    for i, s in enumerate(data.get("sallittu", []), 1):
        if not s.get("peruste", "").strip():
            raise ValueError(f"{polku.name}: kohdasta {i} puuttuu peruste")
        if not isinstance(s.get("voimassa"), date):
            raise ValueError(f"{polku.name}: kohdan {i} voimassa ei ole "
                             "päivämäärä")
        tulos.append(Sallittu(s["koodi"], s["tiedosto"], s["kuvio"],
                              s["peruste"], s["voimassa"]))
    return tulos
# @loppu poikkeus


# @alku luokittele
@dataclass
class Luokittelu:
    uudet: list[Varoitus] = field(default_factory=list)
    sallitut: list[Varoitus] = field(default_factory=list)
    vanhentuneet: list[Varoitus] = field(default_factory=list)
    tarpeettomat: list[Sallittu] = field(default_factory=list)

    @property
    def lapi(self) -> bool:
        """Laatuportti: ei uusia eikä vanhentuneesti sallittuja."""
        return not self.uudet and not self.vanhentuneet


def luokittele(varoitukset: list[Varoitus], sallitut: list[Sallittu],
               paiva: date) -> Luokittelu:
    tulos = Luokittelu()
    kaytetyt: set[Sallittu] = set()
    for v in varoitukset:
        osuma = next((s for s in sallitut if s.koskee(v)), None)
        if osuma is None:
            tulos.uudet.append(v)
        elif osuma.voimassa < paiva:
            tulos.vanhentuneet.append(v)
            kaytetyt.add(osuma)
        else:
            tulos.sallitut.append(v)
            kaytetyt.add(osuma)
    # Sallittu, johon mikään ei osu, on poistettava listalta: muuten se
    # hyväksyisi myöhemmin samannäköisen uuden varoituksen.
    tulos.tarpeettomat = [s for s in sallitut if s not in kaytetyt]
    return tulos
# @loppu luokittele

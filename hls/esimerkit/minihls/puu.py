"""Jäsennyspuu: lähdekielen lausekkeet, lauseet ja funktio.

Lähdekieli on C++:n pieni osajoukko, jonka voi kääntää myös g++:lla
C-simulaatiota varten. Kaikki skalaarit ovat 32-bittisiä int-lukuja.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# @alku lausekkeet
@dataclass(frozen=True)
class Luku:
    arvo: int


@dataclass(frozen=True)
class Nimi:
    nimi: str


@dataclass(frozen=True)
class Indeksi:
    taulu: str
    indeksi: Lauseke


@dataclass(frozen=True)
class Binaari:
    op: str
    vasen: Lauseke
    oikea: Lauseke


@dataclass(frozen=True)
class Unaari:
    op: str
    arvo: Lauseke


@dataclass(frozen=True)
class Ehto:
    ehto: Lauseke
    tosi: Lauseke
    epatosi: Lauseke


@dataclass(frozen=True)
class Lue:
    virta: str


Lauseke = Luku | Nimi | Indeksi | Binaari | Unaari | Ehto | Lue
# @loppu lausekkeet


# @alku lauseet
@dataclass(frozen=True)
class Pragma:
    laji: str                       # pipeline, unroll, array_partition, ...
    asetukset: dict[str, str]
    rivi: int


@dataclass(frozen=True)
class Sijoitus:
    kohde: Nimi | Indeksi
    arvo: Lauseke
    rivi: int


@dataclass(frozen=True)
class Kirjoita:
    virta: str
    arvo: Lauseke
    rivi: int


@dataclass(frozen=True)
class Jos:
    ehto: Lauseke
    tosi: list[Lause]
    epatosi: list[Lause]
    rivi: int


@dataclass(frozen=True)
class Silmukka:
    nimi: str
    muuttuja: str
    alku: int
    askel: int
    kierrokset: int
    runko: list[Lause]
    pragmat: list[Pragma]
    rivi: int


@dataclass(frozen=True)
class Palauta:
    arvo: Lauseke
    rivi: int


Lause = Sijoitus | Kirjoita | Jos | Silmukka | Palauta
# @loppu lauseet


# @alku funktio
@dataclass(frozen=True)
class Parametri:
    nimi: str
    laji: str                       # skalaari, taulu tai virta
    koko: int = 0                   # taulukon alkioiden määrä
    vain_luku: bool = False         # const-taulukko


@dataclass
class Funktio:
    nimi: str
    palauttaa: bool
    parametrit: list[Parametri]
    runko: list[Lause]
    pragmat: list[Pragma]
    paikalliset: dict[str, int] = field(default_factory=dict)
    vakiotaulut: dict[str, list[int]] = field(default_factory=dict)

    def parametri(self, nimi: str) -> Parametri | None:
        for p in self.parametrit:
            if p.nimi == nimi:
                return p
        return None
# @loppu funktio


class KaannosVirhe(Exception):
    """Lähdekoodin virhe, joka ilmoitetaan rivinumeron kanssa."""

    def __init__(self, rivi: int, viesti: str) -> None:
        super().__init__(f"rivi {rivi}: {viesti}")
        self.rivi = rivi

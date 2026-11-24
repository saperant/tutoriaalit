"""Yhteinen tietomalli: kaikkien työkalujen tulokset samassa muodossa."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


# @alku malli
@dataclass(frozen=True)
class Varoitus:
    tyokalu: str
    koodi: str
    tiedosto: str
    rivi: int
    viesti: str


@dataclass(frozen=True)
class Resurssit:
    solut: int
    kiikut: int
    tyypit: dict[str, int]


@dataclass(frozen=True)
class Ajoitus:
    jakso: float
    saapuminen: float
    vaadittu: float
    slack: float
    syvyys: int

    @property
    def kunnossa(self) -> bool:
        return self.slack >= 0


@dataclass(frozen=True)
class SimTulos:
    testi: str
    siemen: int
    tila: str              # "ok", "virhe" tai "aikakatkaisu"
    virheita: int = 0
    viestit: tuple[str, ...] = ()


@dataclass
class Raportti:
    """Yhden ajon kooste. Kentät, joita ajo ei tuottanut, ovat None."""

    lohko: str
    resurssit: Resurssit | None = None
    ajoitus: Ajoitus | None = None
    simuloinnit: list[SimTulos] = field(default_factory=list)
    kattavuus: dict[str, int] = field(default_factory=dict)
    varoitukset: list[Varoitus] = field(default_factory=list)

    def tallenna(self, polku: Path) -> None:
        polku.write_text(json.dumps(asdict(self), indent=2,
                                    sort_keys=True, ensure_ascii=False)
                         + "\n", encoding="utf-8")
# @loppu malli

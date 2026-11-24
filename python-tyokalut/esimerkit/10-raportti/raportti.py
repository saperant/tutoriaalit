"""Regressioajon raportti JSON Lines -tuloksista."""

import json
import os
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, TypedDict, cast

# @alku tyypit
Tila = Literal["läpi", "epäonnistui", "aikaraja"]


class AjoTulos(TypedDict):
    """Yksi rivi tulostiedostossa (JSON-objekti)."""
    testi: str
    siemen: int
    tila: Tila
    kesto_s: float


@dataclass(frozen=True)
class Yhteenveto:
    ajoja: int
    lapi: int
    kesto_s: float
    epaonnistuneet: tuple[str, ...]

    @property
    def lapaisyprosentti(self) -> float:
        return 100.0 * self.lapi / self.ajoja if self.ajoja else 0.0
# @loppu tyypit


# @alku logiikka
def lue(polku: Path) -> list[AjoTulos]:
    tulokset = []
    with polku.open(encoding="utf-8") as f:
        for nro, rivi in enumerate(f, 1):
            data = json.loads(rivi)
            if data.get("tila") not in ("läpi", "epäonnistui", "aikaraja"):
                raise ValueError(f"{polku}:{nro}: tuntematon tila")
            tulokset.append(cast(AjoTulos, data))
    return tulokset


def yhteenveto(tulokset: Iterable[AjoTulos]) -> Yhteenveto:
    lista = list(tulokset)
    huonot = sorted(f"{t['testi']}/{t['siemen']} ({t['tila']})"
                    for t in lista if t["tila"] != "läpi")
    return Yhteenveto(len(lista), len(lista) - len(huonot),
                      round(sum(t["kesto_s"] for t in lista), 1),
                      tuple(huonot))


def nyt() -> datetime:
    return datetime.now(UTC)


def muotoile(y: Yhteenveto) -> str:
    otsikko = os.environ.get("RAPORTTI_OTSIKKO", "Regressioajo")
    rivit = [f"{otsikko} {nyt():%Y-%m-%d %H:%M} UTC",
             f"läpi {y.lapi}/{y.ajoja} ({y.lapaisyprosentti:.1f} %), "
             f"kesto yhteensä {y.kesto_s} s"]
    rivit += [f"  EPÄONNISTUI {nimi}" for nimi in y.epaonnistuneet]
    return "\n".join(rivit) + "\n"
# @loppu logiikka

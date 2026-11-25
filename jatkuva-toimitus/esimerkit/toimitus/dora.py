"""Toimituskyvyn neljä mittaria julkaisuhistoriasta.

Mittarit ovat DORA-tutkimusohjelman käyttämät: toimitustiheys, muutoksen
läpimenoaika, muutosten epäonnistumisosuus ja palautumisaika. Kaksi
ensimmäistä kuvaa nopeutta, kaksi jälkimmäistä vakautta.
"""

from dataclasses import dataclass
from datetime import datetime
from statistics import median


# @alku mittarit
@dataclass(frozen=True)
class Julkaisu:
    hetki: datetime                      # käyttöönotto tuotantoon
    muutokset: tuple[datetime, ...]      # julkaisun commitien hetket
    korjattu: datetime | None = None     # None: julkaisu onnistui


@dataclass(frozen=True)
class Mittarit:
    tiheys: float            # julkaisua viikossa
    lapimeno: float          # tuntia commitista tuotantoon, mediaani
    epaonnistui: float       # osuus julkaisuista, joka vaati korjauksen
    palautuminen: float      # tuntia viasta korjaukseen, mediaani


def laske(julkaisut: list[Julkaisu], viikkoja: float) -> Mittarit:
    lapimenot = [(j.hetki - m).total_seconds() / 3600
                 for j in julkaisut for m in j.muutokset]
    palautumiset = [(j.korjattu - j.hetki).total_seconds() / 3600
                    for j in julkaisut if j.korjattu is not None]
    return Mittarit(
        tiheys=len(julkaisut) / viikkoja,
        lapimeno=median(lapimenot),
        epaonnistui=len(palautumiset) / len(julkaisut),
        palautuminen=median(palautumiset) if palautumiset else 0.0)
# @loppu mittarit


def rivi(nimi: str, m: Mittarit) -> str:
    return (f"{nimi:<22}{m.tiheys:>8.1f}{m.lapimeno:>10.0f}"
            f"{m.epaonnistui:>11.0%}{m.palautuminen:>10.1f}")


OTSIKKO = (f"{'':<22}{'julk./vk':>8}{'läpim. h':>10}"
           f"{'epäonn.':>11}{'palaut. h':>10}")

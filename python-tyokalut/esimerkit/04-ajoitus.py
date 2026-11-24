"""Staattisen ajoitusanalyysin raportin jäsentäminen tilakoneella.

Raportissa polku on usean rivin lohko. Yksi säännöllinen lauseke ei
riitä, joten jäsennin muistaa, missä lohkossa se on, ja kerää kentät
polku kerrallaan."""

import enum
import re
import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class Polku:
    alku: str
    loppu: str
    ryhma: str
    saapuminen: float
    slack: float


# @alku tilakone
class Tila(enum.Enum):
    VALISSA = enum.auto()   # polkujen välissä
    POLUSSA = enum.auto()   # polkulohkon sisällä


KENTTA = re.compile(r"^\s*(Startpoint|Endpoint|Path Group):\s*(\S+)")
SAAPUMINEN = re.compile(r"^\s*data arrival time\s+(-?\d+\.\d+)")
SLACK = re.compile(r"^\s*slack \((MET|VIOLATED)\)\s+(-?\d+\.\d+)")


def polut(rivit: Iterable[str]) -> Iterator[Polku]:
    tila = Tila.VALISSA
    kentat: dict[str, str] = {}
    saapuminen = 0.0
    for nro, rivi in enumerate(rivit, 1):
        if m := KENTTA.match(rivi):
            if m[1] == "Startpoint":
                if tila is Tila.POLUSSA:
                    raise ValueError(f"rivi {nro}: edellinen polku kesken")
                tila, kentat = Tila.POLUSSA, {}
            kentat[m[1]] = m[2]
        elif tila is Tila.POLUSSA and (m := SAAPUMINEN.match(rivi)):
            saapuminen = float(m[1])
        elif tila is Tila.POLUSSA and (m := SLACK.match(rivi)):
            yield Polku(kentat["Startpoint"], kentat["Endpoint"],
                        kentat.get("Path Group", "?"), saapuminen,
                        float(m[2]))
            tila = Tila.VALISSA
    if tila is Tila.POLUSSA:
        raise ValueError("raportti loppui kesken polun")
# @loppu tilakone


def main() -> int:
    kaikki = sorted(polut(sys.stdin), key=lambda p: p.slack)
    rikkovat = [p for p in kaikki if p.slack < 0]
    print(f"polkuja {len(kaikki)}, rikkovia {len(rikkovat)}, "
          f"WNS {kaikki[0].slack:+.2f} ns, "
          f"TNS {sum(p.slack for p in rikkovat):+.2f} ns")
    for p in kaikki[:3]:
        print(f"{p.slack:+6.2f}  {p.alku} -> {p.loppu} ({p.ryhma})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

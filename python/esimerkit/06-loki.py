"""Lokin käsittely laiskana generaattoriputkena."""

import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass


# @alku putki
@dataclass(frozen=True)
class Pyynto:
    polku: str
    tila: int
    kesto_ms: int


def jasenna(rivit: Iterable[str]) -> Iterator[Pyynto]:
    for rivi in rivit:
        osat = rivi.split()
        if len(osat) != 3:
            continue                     # rikkinäinen rivi ohitetaan
        polku, tila, kesto = osat
        yield Pyynto(polku, int(tila), int(kesto))


def virheelliset(pyynnot: Iterable[Pyynto]) -> Iterator[Pyynto]:
    return (p for p in pyynnot if p.tila >= 500)


def hitaat(pyynnot: Iterable[Pyynto], raja_ms: int) -> Iterator[Pyynto]:
    yield from (p for p in pyynnot if p.kesto_ms > raja_ms)
# @loppu putki


# @alku kaytto
# Putki käsittelee yhden rivin kerrallaan: koko lokia ei ladata muistiin.
for pyynto in hitaat(virheelliset(jasenna(sys.stdin)), raja_ms=200):
    print(f"{pyynto.polku} {pyynto.tila} {pyynto.kesto_ms} ms")
# @loppu kaytto

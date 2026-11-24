"""Avainten jako solmuille: modulo, konsistentti hajautus ja rendezvous.

Kaikki käyttävät samaa tiivistettä. Pythonin oma hash() vaihtuu
prosessista toiseen (PYTHONHASHSEED), joten sitä ei voi käyttää jakoon,
jonka täytyy olla sama kaikilla palvelimilla.
"""

from __future__ import annotations

import bisect
import hashlib
from collections.abc import Iterable


def tiiviste(avain: str) -> int:
    """64-bittinen, tasaisesti jakautuva ja kaikkialla sama."""
    return int.from_bytes(hashlib.sha256(avain.encode()).digest()[:8],
                          "big")


# @alku modulo
class Modulo:
    """solmu = tiiviste mod n: tasainen, mutta solmun lisäys siirtää
    lähes kaikki avaimet."""

    def __init__(self, solmut: Iterable[str]) -> None:
        self.solmut = list(solmut)

    def solmu(self, avain: str) -> str:
        return self.solmut[tiiviste(avain) % len(self.solmut)]
# @loppu modulo


# @alku rengas
class Rengas:
    """Konsistentti hajautus: solmut ja avaimet samalle 64-bittiselle
    kehälle. Avain kuuluu ensimmäiselle solmulle myötäpäivään. Jokaisella
    solmulla on useita virtuaalisolmuja, jotta osuudet tasoittuvat."""

    def __init__(self, solmut: Iterable[str], virtuaaleja: int = 100
                 ) -> None:
        self.virtuaaleja = virtuaaleja
        self._pisteet: list[int] = []
        self._omistaja: dict[int, str] = {}
        for solmu in solmut:
            self.lisaa(solmu)

    def lisaa(self, solmu: str) -> None:
        for i in range(self.virtuaaleja):
            piste = tiiviste(f"{solmu}#{i}")
            bisect.insort(self._pisteet, piste)
            self._omistaja[piste] = solmu

    def poista(self, solmu: str) -> None:
        for i in range(self.virtuaaleja):
            piste = tiiviste(f"{solmu}#{i}")
            self._pisteet.remove(piste)
            del self._omistaja[piste]

    def solmu(self, avain: str) -> str:
        i = bisect.bisect(self._pisteet, tiiviste(avain))
        return self._omistaja[self._pisteet[i % len(self._pisteet)]]
# @loppu rengas


# @alku rendezvous
class Rendezvous:
    """Suurimman painon hajautus: avain kuuluu solmulle, jonka
    tiiviste(solmu, avain) on suurin. Ei virtuaalisolmuja eikä kehää,
    mutta haku käy läpi kaikki solmut."""

    def __init__(self, solmut: Iterable[str]) -> None:
        self.solmut = list(solmut)

    def solmu(self, avain: str) -> str:
        return max(self.solmut, key=lambda s: tiiviste(f"{s}|{avain}"))
# @loppu rendezvous

"""Sidonta: operaatiot laitteistoyksiköille ja arvot rekistereille."""

from __future__ import annotations

from dataclasses import dataclass, field

from .ajoitus import Ajoitus
from .dfg import Dfg, Viite, operandit


@dataclass
class Lehtiajoitus:
    """Yhden lehden graafi ja ajoitus sekä johdetut tiedot."""
    numero: int
    nimi: str
    g: Dfg
    t: Ajoitus
    kierrokset: int
    alku: int
    askel: int
    pyydetty_ii: int | None
    syyt: list[str] = field(default_factory=list)

    @property
    def ii(self) -> int:
        return self.t.ii

    @property
    def vaiheet(self) -> int:
        return -(-self.t.pituus // self.ii)

    @property
    def latenssi(self) -> int:
        return (self.kierrokset + self.vaiheet - 1) * self.ii

    def vaihe(self, jakso: int) -> int:
        return jakso // self.ii


# @alku yksikot
def sido_kertojat(lehdet: list[Lehtiajoitus]) -> dict[int, int]:
    """Jakaa kertolaskut kertojayksiköille. Yksikkö voi palvella useaa
    operaatiota, jos ne ovat eri jaksoissa (liukuhihnassa: eri jaksoissa
    mod II) tai eri lehdissä, koska lehdet suoritetaan peräkkäin."""
    varaukset: list[set[tuple[int, int]]] = []
    sidonta: dict[int, int] = {}
    for lehti in lehdet:
        kertolaskut = sorted((lehti.t.jakso[i], i)
                             for i, s in lehti.g.solmut.items()
                             if s.laji == "*")
        for jakso, i in kertolaskut:
            paikka = (lehti.numero, jakso % lehti.ii)
            vapaat = [n for n, v in enumerate(varaukset) if paikka not in v]
            numero = vapaat[0] if vapaat else len(varaukset)
            if not vapaat:
                varaukset.append(set())
            varaukset[numero].add(paikka)
            sidonta[i] = numero
    return sidonta
# @loppu yksikot


# @alku rekisterit
def rekisterit(lehti: Lehtiajoitus) -> dict[int, tuple[int, int]]:
    """Arvot, jotka on säilytettävä rekisterissä: solmu -> (ensimmäinen,
    viimeinen vaihe). Arvo kirjoitetaan rekisteriin jaksolla, jolloin se
    on johdossa, ja siirretään vaiheesta seuraavaan kierroksen lopussa,
    koska liukuhihnassa on samaan aikaan useita kierroksia."""
    g, t = lehti.g, lehti.t
    tulos: dict[int, tuple[int, int]] = {}
    for s in g.solmut.values():
        for o in operandit(s):
            if not isinstance(o, Viite):
                continue
            u = o.solmu
            if t.jakso[s.id] <= t.johto[u]:
                continue
            ensin = lehti.vaihe(t.johto[u] + 1)
            viimeinen = lehti.vaihe(t.jakso[s.id])
            if u in tulos:
                ensin = min(ensin, tulos[u][0])
                viimeinen = max(viimeinen, tulos[u][1])
            tulos[u] = (ensin, viimeinen)
    return tulos
# @loppu rekisterit

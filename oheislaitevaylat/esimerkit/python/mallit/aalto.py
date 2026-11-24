"""Aaltomuodot tekstinä: logiikka-analysaattorin näkymä päätteessä.

Jokainen signaali piirretään kahdelle riville. Ylätaso (1) näkyy
ylemmän rivin alaviivana ja alataso (0) alemman rivin alaviivana;
pystyviiva merkitsee tason muutosta:

    SCL ___     ___
           |___|   |___
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

LEVEYS = 64  # aika-askelia riviä kohti ennen rivitystä


# @alku aalto
@dataclass
class Aalto:
    """Signaalien tasot aika-askelittain ja askeliin liitetyt merkinnät
    (esim. bitin arvo tai kentän nimi)."""

    nimet: Sequence[str]
    naytteet: list[tuple[int, ...]] = field(default_factory=list)
    merkinnat: dict[int, str] = field(default_factory=dict)

    def lisaa(self, *tasot: int, merkinta: str = "") -> None:
        if len(tasot) != len(self.nimet):
            raise ValueError("tasojen maara ei vastaa signaaleja")
        if merkinta:
            self.merkinnat[len(self.naytteet)] = merkinta
        self.naytteet.append(tasot)

    def signaali(self, nimi: str) -> list[int]:
        i = list(self.nimet).index(nimi)
        return [n[i] for n in self.naytteet]

    def osa(self, alku: int, loppu: int) -> "Aalto":
        merkinnat = {t - alku: m for t, m in self.merkinnat.items()
                     if alku <= t < loppu}
        return Aalto(self.nimet, self.naytteet[alku:loppu], merkinnat)
    # @loppu aalto

    def piirra(self, askel: int = 2, leveys: int = LEVEYS) -> str:
        """Piirtää aallon; askel on merkkiä aika-askelta kohti. Pitkät
        aallot rivitetään."""
        nimileveys = max(len(n) for n in self.nimet) + 1
        lohkot = []
        for alku in range(0, len(self.naytteet), leveys // askel):
            loppu = min(alku + leveys // askel, len(self.naytteet))
            rivit = []
            for i, nimi in enumerate(self.nimet):
                yla, ala = self._rivit(i, alku, loppu, askel)
                rivit.append(" " * nimileveys + yla.rstrip())
                rivit.append(nimi.ljust(nimileveys) + ala.rstrip())
            if any(alku <= t < loppu for t in self.merkinnat):
                rivit.append(" " * nimileveys
                             + self._merkinnat(alku, loppu, askel))
            lohkot.append("\n".join(rivit))
        return "\n\n".join(lohkot)

    def _rivit(self, i: int, alku: int, loppu: int,
               askel: int) -> tuple[str, str]:
        yla: list[str] = []
        ala: list[str] = []
        edellinen = self.naytteet[alku][i]
        for t in range(alku, loppu):
            taso = self.naytteet[t][i]
            for k in range(askel):
                vaihtuu = k == 0 and taso != edellinen
                yla.append("_" if taso else " ")
                ala.append("|" if vaihtuu else ("_" if not taso else " "))
            edellinen = taso
        return "".join(yla), "".join(ala)

    def _merkinnat(self, alku: int, loppu: int, askel: int) -> str:
        rivi: list[str] = []
        for t in sorted(self.merkinnat):
            if not alku <= t < loppu:
                continue
            paikka = (t - alku) * askel
            teksti = self.merkinnat[t]
            if len(rivi) > paikka:
                continue  # päällekkäinen merkintä jätetään pois
            rivi.extend(" " * (paikka - len(rivi)))
            rivi.extend(teksti)
        return "".join(rivi).rstrip()

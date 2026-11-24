"""Tapahtumapohjainen porttitason simulaattori.

Piiri koostuu porteista, joilla on viive. Kun signaali muuttuu, sitä
kuuntelevien porttien lähtö lasketaan uudelleen, ja uusi arvo
ajastetaan tapahtumaksi viiveen päähän. Viive on kuljetusviive: jokainen
muutos etenee, myös lyhyt piikki. Näin simulaattori näyttää viiveet ja
hasardit, joita pelkkä totuustaulu ei näytä.

Muut esimerkit tuovat tämän modulin (`from porttisim import Piiri`).
Suoraan ajettuna se näyttää kolmen invertterin ketjun viiveen.
"""

from __future__ import annotations

import heapq
from collections.abc import Callable, Sequence
from dataclasses import dataclass

# @alku portit
Funktio = Callable[[Sequence[int]], int]

PORTIT: dict[str, Funktio] = {
    "NOT": lambda x: 1 - x[0],
    "AND": lambda x: int(all(x)),
    "OR": lambda x: int(any(x)),
    "NAND": lambda x: 1 - int(all(x)),
    "NOR": lambda x: 1 - int(any(x)),
    "XOR": lambda x: sum(x) % 2,
}


@dataclass
class Portti:
    tyyppi: str
    tulot: list[str]
    lahto: str
    viive: int
# @loppu portit


# @alku piiri
class Piiri:
    def __init__(self) -> None:
        self.arvot: dict[str, int] = {}
        self.kuuntelijat: dict[str, list[Portti]] = {}
        self.portit: list[Portti] = []
        self.jono: list[tuple[int, int, str, int]] = []
        self.aika = 0
        self.jarjestys = 0          # saman hetken tapahtumien järjestys
        self.muutokset: list[tuple[int, str, int]] = []

    def portti(self, tyyppi: str, tulot: list[str], lahto: str,
               viive: int = 1) -> None:
        p = Portti(tyyppi, tulot, lahto, viive)
        self.portit.append(p)
        for s in [*tulot, lahto]:
            self.arvot.setdefault(s, 0)
        for s in tulot:
            self.kuuntelijat.setdefault(s, []).append(p)

    def aseta(self, signaali: str, arvo: int, aika: int) -> None:
        """Ajastaa ulkoisen syötteen muutoksen."""
        self._ajasta(aika, signaali, arvo)

    def _ajasta(self, aika: int, signaali: str, arvo: int) -> None:
        heapq.heappush(self.jono, (aika, self.jarjestys, signaali, arvo))
        self.jarjestys += 1

    def aja(self, loppu: int) -> None:
        """Käsittelee tapahtumat hetkeen `loppu` asti."""
        while self.jono and self.jono[0][0] <= loppu:
            aika, _, signaali, arvo = heapq.heappop(self.jono)
            self.aika = aika
            if self.arvot[signaali] == arvo:
                continue            # ei muutosta, ei tapahtumaa
            self.arvot[signaali] = arvo
            self.muutokset.append((aika, signaali, arvo))
            for p in self.kuuntelijat.get(signaali, []):
                uusi = PORTIT[p.tyyppi]([self.arvot[s] for s in p.tulot])
                self._ajasta(aika + p.viive, p.lahto, uusi)
        self.aika = loppu

    def alusta(self, signaali: str, arvo: int) -> None:
        """Asettaa signaalin alkuarvon ilman tapahtumaa (esim. salvan
        tila)."""
        self.arvot[signaali] = arvo

    def asetu(self) -> None:
        """Laskee kaikki portit ja antaa piirin asettua ennen koetta.
        Koe alkaa sen jälkeen hetkestä 0."""
        for p in self.portit:
            uusi = PORTIT[p.tyyppi]([self.arvot[s] for s in p.tulot])
            self._ajasta(self.aika, p.lahto, uusi)
        self.aja(self.aika + 1000)
        if self.jono:
            raise RuntimeError("piiri ei asetu: se värähtelee")
        self.aika = 0
        self.muutokset.clear()
# @loppu piiri

    # @alku aaltomuoto
    def aaltomuoto(self, signaalit: list[str], loppu: int) -> str:
        """Piirtää signaalit tekstinä: yksi merkki aikayksikköä kohden."""
        rivit = []
        for s in signaalit:
            arvo = self._alkuarvo(s)
            merkit = []
            for t in range(loppu):
                for aika, nimi, uusi in self.muutokset:
                    if aika == t and nimi == s:
                        arvo = uusi
                merkit.append(str(arvo))
            rivit.append(f"{s:>6} {''.join(merkit)}")
        return "\n".join(rivit)

    def _alkuarvo(self, signaali: str) -> int:
        for _, nimi, arvo in self.muutokset:
            if nimi == signaali:
                return 1 - arvo     # ensimmäistä muutosta edeltävä arvo
        return self.arvot[signaali]
    # @loppu aaltomuoto


if __name__ == "__main__":
    # @alku ketju
    piiri = Piiri()
    piiri.portti("NOT", ["a"], "b", viive=2)
    piiri.portti("NOT", ["b"], "c", viive=2)
    piiri.portti("NOT", ["c"], "d", viive=2)
    piiri.asetu()
    piiri.aseta("a", 1, aika=2)
    piiri.aja(14)
    print("aika   0         1")
    print("       01234567890123")
    print(piiri.aaltomuoto(["a", "b", "c", "d"], 14))
    # @loppu ketju

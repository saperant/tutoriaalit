"""FIFOn verifiointiympäristö cocotbille: transaktio, ajuri, monitori,
referenssimalli, tulostaulu ja kattavuusmalli.

DUT-kahva on tyypiltään Any: cocotb luo signaalien kahvat ajon aikana,
joten tyyppitarkistin ei näe niitä.
"""

from __future__ import annotations

import os
import random
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cocotb.triggers import FallingEdge, RisingEdge

from kattavuus import Kattavuuspiste, Ristikattavuus

SYVYYS = 4


def raportti(rivi: str) -> None:
    """Kirjaa testin havainnon tiedostoon, jonka ajaja tulostaa."""
    polku = os.environ.get("RAPORTTI")
    if polku:
        with Path(polku).open("a", encoding="utf-8") as f:
            f.write(rivi + "\n")


# @alku transaktio
@dataclass(frozen=True)
class Toimenpide:
    """Yhden kellojakson toimenpide FIFOn liitännässä."""

    push: bool
    pop: bool
    data: int = 0
    # @loppu transaktio


# @alku malli
class FifoMalli:
    """Referenssimalli: mitä FIFOn pitää tehdä, ilman ajoitusta."""

    def __init__(self, syvyys: int = SYVYYS) -> None:
        self.syvyys = syvyys
        self.jono: deque[int] = deque()

    def askel(self, t: Toimenpide) -> int | None:
        """Päivittää tilan; palauttaa luetun arvon tai None.

        Kirjoitus ja luku päätetään jakson alun tilasta, kuten RTL:ssä:
        täyteen jonoon ei kirjoiteta, vaikka samalla luettaisiin.
        """
        kirjoita = t.push and len(self.jono) < self.syvyys
        luettu = self.jono.popleft() if t.pop and self.jono else None
        if kirjoita:
            self.jono.append(t.data)
        return luettu
        # @loppu malli


# @alku ajuri
class FifoAjuri:
    """Vie toimenpiteet liitäntään laskevalla kellon reunalla."""

    def __init__(self, dut: Any) -> None:
        self.dut = dut

    async def aja(self, t: Toimenpide) -> None:
        await FallingEdge(self.dut.clk)
        self.dut.push.value = int(t.push)
        self.dut.pop.value = int(t.pop)
        self.dut.din.value = t.data

    async def lepo(self) -> None:
        await self.aja(Toimenpide(push=False, pop=False))
        # @loppu ajuri


# @alku monitori
@dataclass(frozen=True)
class Havainto:
    """Mitä liitännässä tapahtui yhdellä nousevalla reunalla."""

    toimenpide: Toimenpide
    dout: int
    tyhja: bool
    taysi: bool
    maara: int


class FifoMonitori:
    """Lukee liitännän tilan nousevalla reunalla.

    Heti RisingEdge-tapahtuman jälkeen rekisterit eivät ole vielä
    päivittyneet, joten havainto on sama, jonka DUT näkee reunalla.
    """

    def __init__(self, dut: Any) -> None:
        self.dut = dut

    async def seuraava(self) -> Havainto:
        await RisingEdge(self.dut.clk)
        d = self.dut
        t = Toimenpide(
            bool(d.push.value), bool(d.pop.value), int(d.din.value)
        )
        # Tyhjän jonon lukupää osoittaa kirjoittamattomaan muistiin (X).
        dout = d.dout.value
        return Havainto(
            t,
            int(dout) if dout.is_resolvable else -1,
            bool(d.tyhja.value),
            bool(d.taysi.value),
            int(d.maara.value),
        )
        # @loppu monitori


# @alku tulostaulu
class Tulostaulu:
    """Vertaa jokaista havaintoa referenssimalliin."""

    def __init__(self) -> None:
        self.malli = FifoMalli()
        self.virheet: list[str] = []
        self.lukuja = 0

    def tarkista(self, h: Havainto) -> None:
        m = self.malli
        if h.maara != len(m.jono):
            self.vika(f"maara={h.maara}, mallissa {len(m.jono)}")
        if h.tyhja != (len(m.jono) == 0):
            self.vika(f"tyhja={int(h.tyhja)}, mallissa {len(m.jono)}")
        if h.taysi != (len(m.jono) == m.syvyys):
            self.vika(f"taysi={int(h.taysi)}, mallissa {len(m.jono)}")
        odotettu = m.jono[0] if m.jono else None
        luettu = m.askel(h.toimenpide)
        if luettu is not None:
            self.lukuja += 1
            if h.dout != odotettu:
                self.vika(f"luettiin {h.dout:02x}, odotettiin {luettu:02x}")

    def vika(self, viesti: str) -> None:
        self.virheet.append(viesti)
        # @loppu tulostaulu


# @alku kattavuus
def fifo_kattavuus() -> tuple[Kattavuuspiste, Kattavuuspiste, Ristikattavuus]:
    """Täyttöaste, toimenpide ja niiden risti."""
    taytto = Kattavuuspiste(
        "tayttoaste",
        {
            "tyhja": lambda m: m == 0,
            "osittain": lambda m: 0 < m < SYVYYS,
            "taysi": lambda m: m == SYVYYS,
        },
    )
    toimi = Kattavuuspiste(
        "toimenpide",
        {
            "lepo": lambda k: k == 0,
            "push": lambda k: k == 1,
            "pop": lambda k: k == 2,
            "push+pop": lambda k: k == 3,
        },
    )
    return taytto, toimi, Ristikattavuus("tila*toimenpide", taytto, toimi)
    # @loppu kattavuus


# @alku generaattori
def satunnainen(
    rng: random.Random, n: int, kunnioita_tyhjaa: bool = True
) -> list[Toimenpide]:
    """Satunnaiset toimenpiteet painotuksin.

    Kun kunnioita_tyhjaa on tosi, generaattori ei lue tyhjästä
    jonosta, kuten moni käsin kirjoitettu generaattori. Tilaa se ei
    kuitenkaan tiedä, joten se arvioi täyttöasteen omalla laskurillaan.
    """
    toimet = []
    arvio = 0
    for _ in range(n):
        r = rng.random()
        push = r < 0.6
        pop = 0.4 <= r < 0.9
        if kunnioita_tyhjaa and arvio == 0:
            pop = False
        toimet.append(Toimenpide(push, pop, rng.randrange(256)))
        arvio = max(0, min(SYVYYS, arvio + int(push) - int(pop)))
    return toimet
    # @loppu generaattori

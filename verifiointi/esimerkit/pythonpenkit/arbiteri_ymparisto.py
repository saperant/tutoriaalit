# @alku vastaavuus
"""Arbiterin verifiointiympäristö UVM:n rakenteella (luku 9).

UVM:n osat ja niiden vastineet tässä tiedostossa:

  uvm_sequence_item   Kohde: uudet pyynnöt yhdellä jaksolla
  uvm_sequence        sekvenssi: generaattori, joka tuottaa kohteita
  uvm_sequencer       Sekvensseri: jono sekvenssin ja ajurin välissä
  uvm_driver          Ajuri: vie kohteet liitäntään
  uvm_monitor         Monitori: havainnoi liitäntää ja julkaisee
  uvm_analysis_port   Monitori.tilaajat: lista vastaanottajia
  uvm_scoreboard      Tarkastaja: vertaa referenssimalliin
  uvm_subscriber      Kattavuus: kerää toiminnallista kattavuutta
  uvm_agent           Agentti: sekvensseri, ajuri ja monitori
  uvm_env             Ymparisto: agentti, tarkastaja ja kattavuus
"""
# @loppu vastaavuus

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any

import cocotb
from cocotb.queue import Queue
from cocotb.triggers import FallingEdge, RisingEdge

from kattavuus import Kattavuuspiste

PYYTAJIA = 4
ODOTUS_RAJA = PYYTAJIA  # pisin sallittu odotus jaksoina


# @alku kohde
@dataclass(frozen=True)
class Kohde:
    """Sekvenssin kohde: pyytäjät, jotka nostavat pyynnön tällä
    jaksolla. Pyyntö pysyy voimassa, kunnes se myönnetään."""

    uudet: int  # bittimaski


@dataclass(frozen=True)
class Havainto:
    jakso: int
    pyynto: int
    myonto: int
    # @loppu kohde


# @alku sekvensseri
class Sekvensseri:
    """Välittää kohteet sekvenssiltä ajurille yksi kerrallaan.

    Jonon koko on yksi, joten sekvenssi odottaa, kunnes ajuri on
    ottanut edellisen kohteen (UVM:ssä get_next_item ja item_done).
    """

    def __init__(self) -> None:
        self.jono: Queue[Kohde | None] = Queue(maxsize=1)

    async def aja(self, sekvenssi: Iterator[Kohde]) -> None:
        for kohde in sekvenssi:
            await self.jono.put(kohde)
        await self.jono.put(None)  # sekvenssi päättyi
        # @loppu sekvensseri


# @alku ajuri
class Ajuri:
    def __init__(self, dut: Any, sekvensseri: Sekvensseri) -> None:
        self.dut = dut
        self.sekvensseri = sekvensseri

    async def aja(self) -> None:
        voimassa = 0
        while True:
            await FallingEdge(self.dut.clk)
            # Myönnetty pyyntö poistuu; uudet kohteet lisäävät pyyntöjä.
            voimassa &= ~int(self.dut.myonto.value)
            kohde = await self.sekvensseri.jono.get()
            if kohde is None:
                self.dut.pyynto.value = 0
                return
            voimassa |= kohde.uudet
            self.dut.pyynto.value = voimassa
            # @loppu ajuri


# @alku monitori
class Monitori:
    """Lukee liitännän nousevalla reunalla ja julkaisee havainnon
    kaikille tilaajille (UVM:n analyysiportti)."""

    def __init__(self, dut: Any) -> None:
        self.dut = dut
        self.tilaajat: list[Callable[[Havainto], None]] = []

    async def aja(self) -> None:
        jakso = 0
        while True:
            await RisingEdge(self.dut.clk)
            jakso += 1
            if int(self.dut.rst.value):
                continue
            h = Havainto(
                jakso, int(self.dut.pyynto.value), int(self.dut.myonto.value)
            )
            for tilaaja in self.tilaajat:
                tilaaja(h)
                # @loppu monitori


# @alku malli
def ennusta(pyynto: int, viimeisin: int) -> tuple[int, int]:
    """Referenssimalli: seuraava myöntö ja uusi viimeisin pyytäjä."""
    for i in range(1, PYYTAJIA + 1):
        ehdokas = (viimeisin + i) % PYYTAJIA
        if pyynto >> ehdokas & 1:
            return 1 << ehdokas, ehdokas
    return 0, viimeisin
    # @loppu malli


# @alku tarkastaja
class Tarkastaja:
    """Vertaa myöntöä malliin ja valvoo yksikuumuutta ja odotusaikaa.
    Virheviestin alussa on luokka hakasulkeissa (luku 10)."""

    def __init__(self) -> None:
        self.viimeisin = PYYTAJIA - 1
        self.odotettu = 0
        self.odotus = [0] * PYYTAJIA
        self.virheet: list[str] = []
        self.myonnetty = 0

    def vika(self, luokka: str, h: Havainto, viesti: str) -> None:
        self.virheet.append(f"[{luokka}] jakso {h.jakso}: {viesti}")

    def kirjaa(self, h: Havainto) -> None:
        if h.myonto & (h.myonto - 1):
            self.vika("yksikuuma", h, f"myonto={h.myonto:04b}")
        elif h.myonto != self.odotettu:
            self.vika(
                "malli",
                h,
                f"myonto={h.myonto:04b}, malli {self.odotettu:04b}",
            )
        self.myonnetty += h.myonto != 0
        for i in range(PYYTAJIA):
            if h.pyynto >> i & 1 and not h.myonto >> i & 1:
                self.odotus[i] += 1
                if self.odotus[i] == ODOTUS_RAJA + 1:
                    self.vika("odotus", h, f"pyytäjä {i} odottaa yli rajan")
            else:
                self.odotus[i] = 0
        # Myöntö näkyy jakson viiveellä: ennuste tämän jakson pyynnöistä.
        self.odotettu, self.viimeisin = ennusta(h.pyynto, self.viimeisin)
        # @loppu tarkastaja


# @alku kattavuus
def arvo_on(n: int) -> Callable[[int], bool]:
    return lambda v: v == n


class Kattavuus:
    def __init__(self) -> None:
        self.kilpailu = Kattavuuspiste(
            "pyyntöjä yhtä aikaa",
            {str(n): arvo_on(n) for n in range(PYYTAJIA + 1)},
        )
        self.saaja = Kattavuuspiste(
            "myönnön saaja",
            {f"p{i}": arvo_on(1 << i) for i in range(PYYTAJIA)},
        )

    def kirjaa(self, h: Havainto) -> None:
        self.kilpailu.havaitse(h.pyynto.bit_count())
        if h.myonto:
            self.saaja.havaitse(h.myonto)
            # @loppu kattavuus


# @alku ymparisto
class Ymparisto:
    """Kokoaa agentin, tarkastajan ja kattavuuden ja kytkee ne."""

    def __init__(self, dut: Any) -> None:
        self.sekvensseri = Sekvensseri()
        self.ajuri = Ajuri(dut, self.sekvensseri)
        self.monitori = Monitori(dut)
        self.tarkastaja = Tarkastaja()
        self.kattavuus = Kattavuus()
        self.monitori.tilaajat += [
            self.tarkastaja.kirjaa,
            self.kattavuus.kirjaa,
        ]

    async def aja(self, sekvenssi: Iterator[Kohde]) -> None:
        monitori = cocotb.start_soon(self.monitori.aja())
        ajuri = cocotb.start_soon(self.ajuri.aja())
        await self.sekvensseri.aja(sekvenssi)
        await ajuri
        await RisingEdge(self.ajuri.dut.clk)  # viimeinen havainto
        monitori.cancel()
        # @loppu ymparisto

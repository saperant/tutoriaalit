"""Virtaliitännän (valid/ready) ajuri ja vastaanottaja cocotbille sekä
tulosten vertailu bittitarkkaan malliin.

Ajuri asettaa tulot laskevalla reunalla ja tarkistaa kättelyn
nousevalla reunalla, jolloin rekisterit eivät ole vielä päivittyneet:
näyte siirtyy, kun s_valid ja s_ready ovat molemmat ykkösiä reunalla.
Satunnaiset tauot (s_valid = 0) ja vastapaine (m_ready = 0) tulevat
siemenestä, joten ajo on toistettavissa.

DUT-kahva on tyypiltään Any: cocotb luo signaalien kahvat ajon aikana.
"""

from __future__ import annotations

import os
import random
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge


def raportti(rivi: str) -> None:
    """Kirjaa havainnon tiedostoon, jonka ajaja tulostaa."""
    polku = os.environ.get("RAPORTTI")
    if polku:
        with Path(polku).open("a", encoding="utf-8") as f:
            f.write(rivi + "\n")


def generaattori(nimi: str) -> random.Random:
    """Testikohtainen satunnaislukugeneraattori: sama siemen ja nimi
    tuottavat aina saman sarjan, vaikka testien järjestys muuttuisi."""
    return random.Random(f"{os.environ.get('SIEMEN', '1')}-{nimi}")


async def aloita(dut: Any) -> None:
    """Kello ja kahden jakson nollaus. Kättelysignaalit nollataan ensin:
    edellisen testin jäljiltä s_valid voi olla yhä ykkönen, jolloin
    DUT ottaisi vastaan vanhan näytteen heti nollauksen jälkeen."""
    Clock(dut.clk, 10, unit="ns").start()
    for nimi in ("s_valid", "m_ready"):
        if hasattr(dut, nimi):
            getattr(dut, nimi).value = 0
    dut.nollaus.value = 1
    await ClockCycles(dut.clk, 2)
    await FallingEdge(dut.clk)
    dut.nollaus.value = 0


def etumerkillinen(kahva: Any) -> int:
    """Signaalin arvo kahden komplementin lukuna."""
    return int(kahva.value.to_signed())


# @alku ajuri
class Ajuri:
    """Syöttää näytteitä liitäntään s_valid/s_ready.

    tauko on todennäköisyys, jolla ajuri pitää ennen näytettä tauon.
    Jokainen näyte on monikko kenttien arvoja, esimerkiksi (s_data,)."""

    def __init__(
        self,
        dut: Any,
        kentat: Sequence[str],
        rng: random.Random,
        tauko: float = 0.3,
    ) -> None:
        self.dut, self.kentat, self.rng, self.tauko = dut, kentat, rng, tauko

    async def laheta(self, naytteet: Sequence[Sequence[int]]) -> None:
        d = self.dut
        for nayte in naytteet:
            await FallingEdge(d.clk)
            while self.rng.random() < self.tauko:
                d.s_valid.value = 0
                await FallingEdge(d.clk)
            for kentta, arvo in zip(self.kentat, nayte, strict=True):
                kahva = getattr(d, kentta)
                kahva.value = arvo & ((1 << len(kahva)) - 1)
            d.s_valid.value = 1
            await RisingEdge(d.clk)
            while not d.s_ready.value:  # odotetaan kättelyä
                await RisingEdge(d.clk)
        await FallingEdge(d.clk)
        d.s_valid.value = 0
        # @loppu ajuri


# @alku vastaanottaja
class Vastaanottaja:
    """Kerää ulostulon näytteet ja pitää satunnaista vastapainetta.

    valmis on todennäköisyys, jolla m_ready on yksi kullakin jaksolla.
    Näyte kirjataan, kun m_valid ja m_ready ovat ykkösiä nousevalla
    reunalla."""

    def __init__(
        self,
        dut: Any,
        kentat: Sequence[str],
        rng: random.Random,
        valmis: float = 0.7,
    ) -> None:
        self.dut, self.kentat, self.rng, self.valmis = (
            dut,
            kentat,
            rng,
            valmis,
        )

    async def keraa(self, n: int, raja: int) -> list[tuple[int, ...]]:
        """n näytettä; AssertionError, jos raja jaksoa ei riitä."""
        d = self.dut
        saatu: list[tuple[int, ...]] = []
        for _ in range(raja):
            await FallingEdge(d.clk)
            d.m_ready.value = int(self.rng.random() < self.valmis)
            await RisingEdge(d.clk)
            if d.m_valid.value and d.m_ready.value:
                saatu.append(
                    tuple(etumerkillinen(getattr(d, k)) for k in self.kentat)
                )
                if len(saatu) == n:
                    return saatu
        raise AssertionError(f"{len(saatu)}/{n} näytettä {raja} jaksossa")
        # @loppu vastaanottaja


# @alku vertaa
def vertaa(
    nimi: str,
    saatu: Sequence[object],
    malli: Sequence[object],
    lisatieto: str = "",
) -> None:
    """Bittitarkka vertailu: jokaisen näytteen on oltava sama kuin
    mallissa. Raportoi erojen määrän ja ensimmäisen eron."""
    erot = [
        i for i, (a, b) in enumerate(zip(saatu, malli, strict=True)) if a != b
    ]
    loppu = f", {lisatieto}" if lisatieto else ""
    if not erot:
        raportti(f"{nimi}: {len(malli)} näytettä bittitarkasti{loppu}")
        return
    i = erot[0]
    raportti(
        f"{nimi}: {len(malli)} näytettä, {len(erot)} eroa; ensimmäinen "
        f"n={i}: RTL {saatu[i]}, malli {malli[i]}"
    )
    raise AssertionError(f"{nimi}: {len(erot)} eroa mallista")
    # @loppu vertaa

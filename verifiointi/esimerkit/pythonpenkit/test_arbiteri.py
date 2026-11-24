"""Arbiterin testit (luku 9). Testi valitsee sekvenssin ja ajaa sen
ympäristössä; ympäristö on kaikille testeille sama."""

from __future__ import annotations

import os
import random
from collections.abc import Iterator
from typing import Any

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

from arbiteri_ymparisto import PYYTAJIA, Kohde, Ymparisto
from fifo_ymparisto import raportti
from kattavuus import raportoi


# @alku sekvenssit
def satunnainen_sekvenssi(rng: random.Random, jaksot: int) -> Iterator[Kohde]:
    """Kukin pyytäjä nostaa pyynnön todennäköisyydellä 0,2."""
    for _ in range(jaksot):
        uudet = sum(1 << i for i in range(PYYTAJIA) if rng.random() < 0.2)
        yield Kohde(uudet)


def kuormitus_sekvenssi(jaksot: int) -> Iterator[Kohde]:
    """Kaikki pyytävät koko ajan: pahin tapaus reiluudelle."""
    for _ in range(jaksot):
        yield Kohde((1 << PYYTAJIA) - 1)
        # @loppu sekvenssit


# @alku testi
async def aja(dut: Any, sekvenssi: Iterator[Kohde], otsikko: str) -> None:
    Clock(dut.clk, 10, unit="ns").start()
    dut.rst.value = 1
    dut.pyynto.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst.value = 0

    ymparisto = Ymparisto(dut)
    await ymparisto.aja(sekvenssi)
    t = ymparisto.tarkastaja
    raportti(f"{otsikko}: {t.myonnetty} myöntöä, {len(t.virheet)} virhettä")
    k = ymparisto.kattavuus
    for rivi in raportoi([k.kilpailu, k.saaja]):
        raportti("  " + rivi)
    assert not t.virheet, t.virheet[0]


@cocotb.test()
async def satunnainen(dut: Any) -> None:
    siemen = int(os.environ.get("SIEMEN", "1"))
    sekvenssi = satunnainen_sekvenssi(random.Random(siemen), 300)
    await aja(dut, sekvenssi, f"satunnainen (siemen {siemen})")


@cocotb.test()
async def kuormitus(dut: Any) -> None:
    await aja(dut, kuormitus_sekvenssi(40), "kuormitus")
    # @loppu testi

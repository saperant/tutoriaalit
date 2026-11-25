"""FIFOn cocotb-testit: ohjattu testi, satunnaistettu testi ja
kulmatapauksia painottava testi. Siemen tulee ympäristömuuttujasta
SIEMEN, jotta epäonnistunut ajo voidaan toistaa."""

from __future__ import annotations

import os
import random
from typing import Any

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

from fifo_ymparisto import (
    SYVYYS,
    FifoAjuri,
    FifoMonitori,
    Toimenpide,
    Tulostaulu,
    fifo_kattavuus,
    raportti,
    satunnainen,
)
from kattavuus import raportoi


# @alku aloitus
async def aloita(dut: Any) -> None:
    """Käynnistää kellon ja pitää nollausta kaksi jaksoa."""
    Clock(dut.clk, 10, unit="ns").start()
    dut.rst.value = 1
    dut.push.value = 0
    dut.pop.value = 0
    dut.din.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst.value = 0
    # @loppu aloitus


# @alku aja
async def aja(dut: Any, toimet: list[Toimenpide], otsikko: str) -> None:
    """Ajaa toimenpiteet ja tarkistaa jokaisen jakson tulostaululla."""
    ajuri, monitori, taulu = FifoAjuri(dut), FifoMonitori(dut), Tulostaulu()
    taytto, toimi, risti = fifo_kattavuus()
    for t in toimet:
        await ajuri.aja(t)
        h = await monitori.seuraava()
        risti.havaitse(h.maara, int(t.push) + 2 * int(t.pop))
        taulu.tarkista(h)
    await ajuri.lepo()
    raportti(
        f"{otsikko}: {len(toimet)} jaksoa, {taulu.lukuja} lukua, "
        f"{len(taulu.virheet)} virhettä"
    )
    for rivi in raportoi([taytto, toimi, risti]):
        raportti("  " + rivi)
    assert not taulu.virheet, taulu.virheet[0]
    # @loppu aja


# @alku ohjattu
@cocotb.test()
async def ohjattu(dut: Any) -> None:
    """Täyttö, ylivuotoyritys ja tyhjennys."""
    await aloita(dut)
    toimet = [Toimenpide(True, False, 0x10 + i) for i in range(SYVYYS + 1)]
    toimet += [Toimenpide(False, True)] * (SYVYYS + 1)
    await aja(dut, toimet, "ohjattu")
    # @loppu ohjattu


# @alku satunnainen
@cocotb.test()
async def satunnaistettu(dut: Any) -> None:
    """Painotettu satunnaistesti, joka ei lue tyhjästä jonosta."""
    siemen = int(os.environ.get("SIEMEN", "1"))
    await aloita(dut)
    toimet = satunnainen(random.Random(siemen), 500)
    await aja(dut, toimet, f"satunnaistettu (siemen {siemen})")
    # @loppu satunnainen


# @alku kulmat
@cocotb.test()
async def kulmat(dut: Any) -> None:
    """Ohjaa satunnaistusta kattavuuden aukkoihin: luku tyhjästä,
    kirjoitus ja luku täyteen jonoon."""
    rng = random.Random(int(os.environ.get("SIEMEN", "1")))
    await aloita(dut)
    toimet = [Toimenpide(False, True), Toimenpide(True, True, 1)]
    for _ in range(20):
        maara = rng.randint(SYVYYS, SYVYYS + 2)  # täyteen ja yli
        toimet += [Toimenpide(True, False, rng.randrange(256))] * maara
        toimet += [
            Toimenpide(True, True, rng.randrange(256)),
            Toimenpide(True, False, rng.randrange(256)),
        ]
        toimet += [Toimenpide(False, True)] * (SYVYYS + 1)  # yli tyhjän
        toimet += [Toimenpide(True, True, rng.randrange(256))]
    await aja(dut, toimet, "kulmat")
    # @loppu kulmat

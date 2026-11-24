"""Luvun 6 UART-lähettimen cocotb-testit.

Ajuri syöttää tavuja valid/ready-kättelyllä, ja monitori purkaa
sarjalinjaa bittitasolla kuten oikea vastaanotin: odottaa
aloitusbitin laskevaa reunaa ja näytteistää jokaisen bitin keskeltä.
Monitori on rinnakkainen korutiini, joten se tarkkailee linjaa koko
ajan, myös silloin kun ajuri odottaa.
"""

from __future__ import annotations

from typing import Any

import cocotb
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge

from apu import kirjaa, satunnainen


# @alku monitori
async def uart_monitori(dut: Any, jakso: int, ulos: Queue[int]) -> None:
    """Purkaa linjalta 8N1-kehyksiä; jakso = kellojaksoa bittiä kohden."""
    while True:
        await FallingEdge(dut.tx)                  # aloitusbitti alkaa
        await ClockCycles(dut.clk, jakso // 2)     # aloitusbitin keskelle
        assert dut.tx.value == 0, "aloitusbitti katkesi (häiriö?)"
        tavu = 0
        for i in range(8):                         # vähiten merkitsevä ensin
            await ClockCycles(dut.clk, jakso)
            tavu |= int(dut.tx.value) << i
        await ClockCycles(dut.clk, jakso)
        assert dut.tx.value == 1, f"lopetusbitti puuttuu (tavu {tavu:#04x})"
        await ulos.put(tavu)
# @loppu monitori


# @alku ajuri
async def laheta(dut: Any, tavu: int) -> None:
    """Antaa tavun lähettimelle: kelvollinen pysyy, kunnes valmis."""
    dut.data.value = tavu
    dut.kelvollinen.value = 1
    while True:
        await RisingEdge(dut.clk)
        if dut.valmis.value == 1:                  # kättely tällä reunalla
            break
    dut.kelvollinen.value = 0
# @loppu ajuri


async def aloita(dut: Any) -> int:
    Clock(dut.clk, 10, unit="ns").start()
    dut.rst_n.value = 0
    dut.kelvollinen.value = 0
    dut.data.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    return int(dut.KELLO_HZ.value) // int(dut.BAUD.value)


# @alku testi
@cocotb.test()
async def satunnaiset_tavut(dut: Any) -> None:
    """Satunnaiset tavut peräkkäin; monitorin tavujen on vastattava."""
    jakso = await aloita(dut)
    vastaanotetut: Queue[int] = Queue()
    cocotb.start_soon(uart_monitori(dut, jakso, vastaanotetut))
    rnd = satunnainen()
    tavut = [0x00, 0xFF, 0x55, 0xAA] + [rnd.randrange(256) for _ in range(12)]
    for tavu in tavut:
        await laheta(dut, tavu)
    saadut = [await vastaanotetut.get() for _ in tavut]
    assert saadut == tavut, f"lähetettiin {tavut}, saatiin {saadut}"
    kirjaa(f"satunnaiset_tavut: {len(tavut)} tavua, {jakso} jaksoa/bitti")
# @loppu testi


@cocotb.test()
async def linja_lepaa(dut: Any) -> None:
    """Ilman dataa linja pysyy ykkösenä ja lähetin on valmis."""
    jakso = await aloita(dut)
    for _ in range(3 * jakso):
        await FallingEdge(dut.clk)
        assert dut.tx.value == 1 and dut.valmis.value == 1
    kirjaa("linja_lepaa: tx = 1 ja valmis = 1")

"""Luvun 6 UART-vastaanottimen cocotb-testit.

Ajuri tuottaa sarjalinjan bittitasolla. Monitori kerää vastaanottimen
`valmis`- ja `kehysvirhe`-pulssit jonoon, josta testit lukevat ne.
"""

from __future__ import annotations

from typing import Any

import cocotb
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge

from apu import kirjaa, satunnainen


# @alku ajuri
async def laheta_kehys(dut: Any, jakso: int, tavu: int,
                       lopetus: int = 1) -> None:
    """Kirjoittaa linjalle 8N1-kehyksen; jakso = kellojaksoa bitille."""
    bitit = [0] + [(tavu >> i) & 1 for i in range(8)] + [lopetus]
    for bitti in bitit:
        dut.rx.value = bitti
        await ClockCycles(dut.clk, jakso)
    dut.rx.value = 1                        # linja lepoon
# @loppu ajuri


# @alku monitori
async def monitori(dut: Any, ulos: Queue[tuple[str, int]]) -> None:
    """Kerää pulssit: ("tavu", arvo) tai ("kehysvirhe", 0)."""
    while True:
        await RisingEdge(dut.clk)
        await FallingEdge(dut.clk)          # rekisterit asettuneet
        if dut.valmis.value == 1:
            await ulos.put(("tavu", int(dut.tavu.value)))
        if dut.kehysvirhe.value == 1:
            await ulos.put(("kehysvirhe", 0))
# @loppu monitori


async def aloita(dut: Any) -> tuple[int, Queue[tuple[str, int]]]:
    Clock(dut.clk, 10, unit="ns").start()
    dut.rx.value = 1
    dut.nollaa.value = 1
    await ClockCycles(dut.clk, 2)
    dut.nollaa.value = 0
    jono: Queue[tuple[str, int]] = Queue()
    cocotb.start_soon(monitori(dut, jono))
    return int(dut.KELLOJA_BITTIIN.value), jono


# @alku testi
@cocotb.test()
async def satunnaiset_tavut(dut: Any) -> None:
    """Satunnaiset tavut; jokaisesta tulee täsmälleen yksi valmis-pulssi."""
    jakso, jono = await aloita(dut)
    rnd = satunnainen()
    tavut = [0x00, 0xFF, 0x55, 0xAA] + [rnd.randrange(256) for _ in range(20)]
    for tavu in tavut:
        await laheta_kehys(dut, jakso, tavu)
        await ClockCycles(dut.clk, rnd.randrange(3 * jakso))  # tauko
    for i, tavu in enumerate(tavut):
        laji, arvo = await jono.get()
        assert (laji, arvo) == ("tavu", tavu), (
            f"tavu {i}: odotettiin {tavu:#04x}, saatiin {laji} {arvo:#04x}")
    assert jono.empty(), "ylimääräisiä pulsseja"
    kirjaa(f"satunnaiset_tavut: {len(tavut)} tavua, {jakso} jaksoa/bitti")
# @loppu testi


@cocotb.test()
async def kehysvirhe(dut: Any) -> None:
    """Lopetusbitti 0 antaa kehysvirheen eikä tavua."""
    jakso, jono = await aloita(dut)
    await laheta_kehys(dut, jakso, 0x3C, lopetus=0)
    await ClockCycles(dut.clk, 2 * jakso)
    assert await jono.get() == ("kehysvirhe", 0)
    await laheta_kehys(dut, jakso, 0xC3)       # seuraava kehys kelpaa
    assert await jono.get() == ("tavu", 0xC3)
    kirjaa("kehysvirhe: virhe tunnistettu, seuraava tavu 0xc3")


# @alku hairio
@cocotb.test()
async def hairiopiikki(dut: Any) -> None:
    """Puolta bittiä lyhyempi nollapulssi ei käynnistä vastaanottoa."""
    jakso, jono = await aloita(dut)
    dut.rx.value = 0
    await ClockCycles(dut.clk, jakso // 4)
    dut.rx.value = 1
    await ClockCycles(dut.clk, 3 * jakso)
    assert jono.empty(), "häiriöpiikki tulkittiin tavuksi"
    kirjaa("hairiopiikki: ei tavua")
# @loppu hairio

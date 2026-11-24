"""Ensimmäinen cocotb-testi: luvun 1 laskuri."""

from __future__ import annotations

from typing import Any

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge

from apu import kirjaa


# @alku testi
@cocotb.test()
async def laskee_sallittuna(dut: Any) -> None:
    """Laskuri kasvaa sallittuna ja pysyy paikallaan muuten."""
    Clock(dut.clk, 10, unit="ns").start()  # 100 MHz
    dut.rst_n.value = 0
    dut.sallittu.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    assert dut.arvo.value == 0

    dut.sallittu.value = 1
    await ClockCycles(dut.clk, 5)
    await FallingEdge(dut.clk)          # luetaan reunojen välissä
    assert dut.arvo.value == 5, f"arvo {int(dut.arvo.value)}"

    dut.sallittu.value = 0
    await ClockCycles(dut.clk, 3)
    assert dut.arvo.value == 5
    kirjaa(f"laskee_sallittuna: arvo {int(dut.arvo.value)}")
# @loppu testi


# @alku ylivuoto
@cocotb.test()
async def kiertaa_ympari(dut: Any) -> None:
    """LEVEYS-bittinen laskuri palaa nollaan 2**LEVEYS askeleen jälkeen."""
    leveys = len(dut.arvo)              # parametri näkyy portin leveydestä
    Clock(dut.clk, 10, unit="ns").start()
    dut.rst_n.value = 0
    dut.sallittu.value = 1
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2**leveys)
    await FallingEdge(dut.clk)
    assert dut.arvo.value == 0
    kirjaa(f"kiertaa_ympari: {leveys} bittiä, {2**leveys} askelta")
# @loppu ylivuoto

"""Luvun 5 kvadratuuridekooderin cocotb-testit.

Testi pyörittää kuviteltua kiertoanturia: jokainen askel muuttaa
kanavia A ja B Gray-järjestyksessä. Malli laskee, mihin asentoon
dekooderin pitäisi päätyä.
"""

from __future__ import annotations

from typing import Any

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge

from apu import kirjaa, satunnainen

# @alku malli
# Kanavien (A, B) arvot myötäpäivään. Askel eteen = seuraava alkio,
# askel taakse = edellinen.
GRAY = [(0, 0), (1, 0), (1, 1), (0, 1)]
VIIVE = 4  # jaksoa: muutos kulkee tahdistimen ja reunantunnistuksen läpi


def kaari(arvo: int) -> int:
    """16-bittisen etumerkillisen laskurin ylivuoto Pythonin luvulle."""
    return (arvo + 2**15) % 2**16 - 2**15
# @loppu malli


async def aloita(dut: Any) -> None:
    Clock(dut.clk, 10, unit="ns").start()
    dut.a.value = 0
    dut.b.value = 0
    dut.nollaa.value = 1
    await ClockCycles(dut.clk, VIIVE)
    dut.nollaa.value = 0
    await FallingEdge(dut.clk)


# @alku testi
@cocotb.test()
async def satunnainen_kiertely(dut: Any) -> None:
    """Satunnaiset askeleet eteen ja taakse; asento seuraa mallia."""
    await aloita(dut)
    rnd = satunnainen()
    vaihe = 0
    odotettu = 0
    for askel in range(300):
        suunta = rnd.choice((1, -1))
        vaihe = (vaihe + suunta) % 4
        odotettu += suunta
        dut.a.value, dut.b.value = GRAY[vaihe]
        # Anturi pysyy asennossa vähintään tahdistuksen viiveen ajan.
        await ClockCycles(dut.clk, VIIVE + rnd.randrange(3))
        await FallingEdge(dut.clk)
        saatu = dut.asento.value.to_signed()
        assert saatu == odotettu, f"askel {askel}: {saatu} != {odotettu}"
    kirjaa(f"satunnainen_kiertely: 300 askelta, asento {odotettu}")
# @loppu testi


@cocotb.test()
async def ylivuoto(dut: Any) -> None:
    """Asento kiertää 16 bitin rajan yli kuten laitteiston laskuri."""
    await aloita(dut)
    vaihe = 0
    for _ in range(2**15 + 2):          # 32 770 askelta taaksepäin
        vaihe = (vaihe - 1) % 4
        dut.a.value, dut.b.value = GRAY[vaihe]
        await ClockCycles(dut.clk, 2)   # askel joka toisella jaksolla
    await ClockCycles(dut.clk, VIIVE)
    await FallingEdge(dut.clk)
    saatu = dut.asento.value.to_signed()
    assert saatu == kaari(-(2**15) - 2), f"asento {saatu}"
    kirjaa(f"ylivuoto: {2**15 + 2} askelta taakse, asento {saatu}")


# @alku hyppy
@cocotb.test()
async def kahden_kanavan_hyppy(dut: Any) -> None:
    """Molempien kanavien samanaikainen muutos ei liikuta asentoa."""
    await aloita(dut)
    dut.a.value, dut.b.value = 1, 1     # 00 -> 11: suunta ei selviä
    await ClockCycles(dut.clk, VIIVE + 2)
    await FallingEdge(dut.clk)
    assert dut.asento.value.to_signed() == 0
    kirjaa("kahden_kanavan_hyppy: asento pysyi 0:ssa")
# @loppu hyppy

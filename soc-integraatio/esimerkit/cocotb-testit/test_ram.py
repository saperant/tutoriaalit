"""RAM:n (AXI4-Lite-orja) cocotb-testit viitemallia vastaan."""

from __future__ import annotations

from typing import Any

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

from apu import kirjaa, satunnainen
from axil import OKAY, AxilIsanta


async def aloita(dut: Any) -> None:
    Clock(dut.kello, 10, unit="ns").start()
    dut.nollaus_n.value = 0
    await ClockCycles(dut.kello, 2)
    dut.nollaus_n.value = 1


def tavumaski(tavut: int) -> int:
    """WSTRB 4 bittiä -> 32-bittinen maski."""
    return sum(0xFF << (8 * t) for t in range(4) if tavut >> t & 1)


# @alku testi
@cocotb.test()
async def satunnaiset_siirrot(dut: Any) -> None:
    """Satunnaiset luvut ja kirjoitukset tavuluvin; malli on sanakirja."""
    await aloita(dut)
    rnd = satunnainen()
    isanta = AxilIsanta(dut, rnd)          # satunnainen vastausviive
    sanat = int(dut.SANAT.value)
    # RAM:ia ei nollata, joten sanat alustetaan ensin kokonaisina:
    # osittainen kirjoitus alustamattomaan sanaan jättäisi X-tavuja.
    malli: dict[int, int] = {}
    for osoite in range(0, 4 * sanat, 4):
        malli[osoite] = rnd.getrandbits(32)
        await isanta.kirjoita(osoite, malli[osoite])
    luvut = kirjoitukset = osittaiset = 0
    for _ in range(300):
        osoite = 4 * rnd.randrange(sanat)
        if rnd.random() < 0.5:
            data = rnd.getrandbits(32)
            tavut = rnd.choice([0xF, 0xF, rnd.randrange(16)])
            assert await isanta.kirjoita(osoite, data, tavut) == OKAY
            m = tavumaski(tavut)
            malli[osoite] = (malli.get(osoite, 0) & ~m) | (data & m)
            kirjoitukset += 1
            osittaiset += tavut != 0xF
        else:
            data, rresp = await isanta.lue(osoite)
            assert rresp == OKAY
            assert data == malli[osoite], (
                f"{osoite:#06x}: {data:#010x} != {malli[osoite]:#010x}")
            luvut += 1
    kirjaa(f"satunnaiset_siirrot: {kirjoitukset} kirjoitusta "
           f"({osittaiset} osittaista), {luvut} lukua")
# @loppu testi


@cocotb.test()
async def perakkaiset(dut: Any) -> None:
    """Kirjoitus ja heti perään luku samaan osoitteeseen ilman viiveitä."""
    await aloita(dut)
    isanta = AxilIsanta(dut)
    for i in range(8):
        await isanta.kirjoita(4 * i, 0x1111_1111 * i)
    for i in range(8):
        assert (await isanta.lue(4 * i))[0] == 0x1111_1111 * i
    kirjaa("perakkaiset: 8 kirjoitusta ja 8 lukua")

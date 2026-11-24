"""GPIO-oheislaitteen (APB-orja) cocotb-testit: rekisterit, virheet ja
keskeytys."""

from __future__ import annotations

from collections import Counter
from typing import Any

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge

from apb import ApbIsanta
from apu import kirjaa, satunnainen

# @alku kartta
ULOS, SISAAN, SALLI, REUNAT = 0x000, 0x004, 0x008, 0x00C
KIRJOITETTAVAT = {ULOS, SALLI}
# @loppu kartta


async def aloita(dut: Any) -> ApbIsanta:
    Clock(dut.kello, 10, unit="ns").start()
    dut.sisaan.value = 0
    dut.nollaus_n.value = 0
    isanta = ApbIsanta(dut)
    await ClockCycles(dut.kello, 2)
    dut.nollaus_n.value = 1
    return isanta


# @alku rekisterit
@cocotb.test()
async def rekisterit_ja_virheet(dut: Any) -> None:
    """Satunnaiset luvut ja kirjoitukset koko osoitealueelle."""
    isanta = await aloita(dut)
    rnd = satunnainen()
    malli = {ULOS: 0, SALLI: 0}
    kattavuus: Counter[tuple[str, str]] = Counter()
    for _ in range(200):
        osoite = rnd.choice([ULOS, SISAAN, SALLI, 0x010, 0xFFC])
        if rnd.random() < 0.5:
            data, tavut = rnd.getrandbits(32), rnd.choice([0xF, 0x1, 0x0])
            virhe = await isanta.kirjoita(osoite, data, tavut)
            # Vain kirjoitettavat rekisterit hyväksyvät kirjoituksen.
            assert virhe == (osoite not in KIRJOITETTAVAT), (
                f"kirjoitus {osoite:#05x}: PSLVERR {int(virhe)}")
            if not virhe and tavut & 1:
                malli[osoite] = data & 0xFF    # 8-bittinen rekisteri
            kattavuus["kirjoitus", "virhe" if virhe else "ok"] += 1
        else:
            data, virhe = await isanta.lue(osoite)
            assert virhe == (osoite not in (ULOS, SISAAN, SALLI)), (
                f"luku {osoite:#05x}: PSLVERR {int(virhe)}")
            if osoite in malli:
                assert data == malli[osoite], f"{osoite:#05x}: {data:#x}"
            kattavuus["luku", "virhe" if virhe else "ok"] += 1
    assert int(dut.ulos.value) == malli[ULOS]
    kirjaa("rekisterit_ja_virheet: siirrot ja vastaukset")
    for (toimi, vastaus), n in sorted(kattavuus.items()):
        kirjaa(f"  {toimi:9} {vastaus:5} {n:3}")
# @loppu rekisterit


# @alku keskeytys
@cocotb.test()
async def keskeytys(dut: Any) -> None:
    """Nouseva reuna sallitussa tulossa nostaa keskeytyksen, W1C kuittaa."""
    isanta = await aloita(dut)
    await isanta.kirjoita(SALLI, 0b0000_0100)    # vain tulo 2 sallittu
    dut.sisaan.value = 0b0000_0001              # tulo 0: ei sallittu
    await ClockCycles(dut.kello, 4)             # tahdistus 2 jaksoa
    await FallingEdge(dut.kello)
    assert dut.keskeytys.value == 0, "kieltämätön tulo nosti keskeytyksen"
    assert (await isanta.lue(REUNAT))[0] == 0b0000_0001

    dut.sisaan.value = 0b0000_0101              # tulo 2 nousee
    await ClockCycles(dut.kello, 4)
    await FallingEdge(dut.kello)
    assert dut.keskeytys.value == 1, "sallittu reuna ei nostanut"
    assert (await isanta.lue(REUNAT))[0] == 0b0000_0101

    await isanta.kirjoita(REUNAT, 0b0000_0100)   # kuittaa vain tulon 2
    await FallingEdge(dut.kello)
    assert dut.keskeytys.value == 0, "keskeytys jäi päälle kuittauksesta"
    assert (await isanta.lue(REUNAT))[0] == 0b0000_0001
    kirjaa("keskeytys: nousi sallitusta reunasta, W1C kuittasi")
# @loppu keskeytys

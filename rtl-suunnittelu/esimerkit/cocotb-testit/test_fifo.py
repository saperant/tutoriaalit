"""Luvun 8 FIFOn cocotb-testit: satunnaistettu testi viitemallia vastaan.

Viitemalli on Pythonin deque. Se on kirjoitettu eri tavalla kuin RTL
(ei osoittimia eikä ylimääräistä bittiä), joten sama ajatusvirhe ei
todennäköisesti ole molemmissa.
"""

from __future__ import annotations

from collections import deque
from itertools import product
from typing import Any

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge

from apu import kirjaa, satunnainen

TILAT = ("tyhja", "osittain", "taynna")
TOIMET = ("lepo", "kirjoitus", "luku", "molemmat")


# @alku aloitus
async def aloita(dut: Any) -> None:
    """Kello käyntiin ja asynkroninen nollaus kahdeksi jaksoksi."""
    Clock(dut.clk, 10, unit="ns").start()
    dut.rst_n.value = 0
    dut.kirjoita.value = 0
    dut.lue.value = 0
    dut.k_data.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
# @loppu aloitus


# @alku testi
@cocotb.test()
@cocotb.parametrize(
    profiili=[("tasainen", 0.5, 0.5), ("tayttava", 0.8, 0.3),
              ("tyhjentava", 0.3, 0.8)],
)
async def satunnaistettu(dut: Any, profiili: tuple[str, float, float]
                         ) -> None:
    """Satunnaiset kirjoitukset ja luvut; tulokset verrataan malliin."""
    nimi, p_kirj, p_luku = profiili
    syvyys = int(dut.SYVYYS.value)
    sanaraja = 2 ** len(dut.k_data)
    # Jokaiselle profiilille omat syötteet, mutta aina samat.
    rnd = satunnainen(lisa=round(100 * p_kirj + 10 * p_luku))
    malli: deque[int] = deque()
    osumat = dict.fromkeys(product(TILAT, TOIMET), 0)
    luettu = 0
    await aloita(dut)

    for _ in range(400):
        await FallingEdge(dut.clk)      # ulostulot ovat asettuneet
        # 1. Ulostulot verrataan malliin.
        maara = len(malli)
        assert dut.tyhja.value == (maara == 0), f"tyhja, {maara} sanaa"
        assert dut.taynna.value == (maara == syvyys), (
            f"taynna, {maara} sanaa")
        if malli:
            assert dut.l_data.value == malli[0], (
                f"luettiin {int(dut.l_data.value)}, odotettiin {malli[0]}")
        # 2. Seuraavan jakson syötteet.
        kirj = rnd.random() < p_kirj
        luku = rnd.random() < p_luku
        data = rnd.randrange(sanaraja)
        dut.kirjoita.value = kirj
        dut.lue.value = luku
        dut.k_data.value = data
        # 3. Malli päivitetään kuten RTL seuraavalla nousevalla reunalla:
        #    molemmat ehdot katsotaan reunaa edeltävästä tilasta.
        tila = ("tyhja" if not malli else
                "taynna" if len(malli) == syvyys else "osittain")
        osumat[tila, TOIMET[kirj + 2 * luku]] += 1
        voi_kirjoittaa = len(malli) < syvyys
        if luku and malli:
            malli.popleft()
            luettu += 1
        if kirj and voi_kirjoittaa:
            malli.append(data)

    katetut = sum(1 for n in osumat.values() if n)
    kirjaa(f"{nimi}: syvyys {syvyys}, luettu {luettu} sanaa, "
           f"kattavuus {katetut}/{len(osumat)}")
# @loppu testi

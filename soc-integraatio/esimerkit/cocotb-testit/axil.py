"""AXI4-Lite-isäntä cocotb-testeihin.

Jokainen viidestä kanavasta (AW, W, B, AR, R) on oma valid/ready-
kättelynsä. Siirto tapahtuu sillä nousevalla reunalla, jolla sekä
VALID että READY ovat ylhäällä. Isäntä ei saa odottaa READY:ä ennen
kuin nostaa VALIDin, ja kerran noussut VALID pysyy ylhäällä kättelyyn
asti; muuten väylä voi lukkiutua.
"""

from __future__ import annotations

import random
from typing import Any

import cocotb
from cocotb.triggers import ClockCycles, RisingEdge

OKAY, SLVERR, DECERR = 0, 2, 3
RAJA = 100  # jaksoa: tätä pidempi odotus on virhe, ei hidas orja


# @alku kattely
async def kattely(dut: Any, valid: Any, ready: Any, kanava: str) -> None:
    """Pitää VALIDin ylhäällä, kunnes READY kuittaa sen reunalla."""
    valid.value = 1
    for _ in range(RAJA):
        await RisingEdge(dut.kello)
        if ready.value == 1:              # arvo juuri ennen reunaa
            valid.value = 0
            return
    raise AssertionError(f"{kanava}: ei kättelyä {RAJA} jaksossa")
# @loppu kattely


class AxilIsanta:
    """Ajaa AXI4-Lite-siirtoja DUT:n signaaleille awaddr, wdata, ..."""

    def __init__(self, dut: Any, rnd: random.Random | None = None):
        self.dut = dut
        self.rnd = rnd  # jos annettu, vastauskanavilla satunnainen viive
        for nimi in ("awvalid", "wvalid", "bready", "arvalid", "rready"):
            getattr(dut, nimi).value = 0

    # @alku kirjoita
    async def kirjoita(self, osoite: int, data: int, tavut: int = 0xF
                       ) -> int:
        """Kirjoittaa sanan; palauttaa BRESP-koodin."""
        d = self.dut
        d.awaddr.value = osoite
        d.wdata.value = data
        d.wstrb.value = tavut
        # AW ja W ovat toisistaan riippumattomia kanavia: rinnakkain.
        aw = cocotb.start_soon(kattely(d, d.awvalid, d.awready, "AW"))
        w = cocotb.start_soon(kattely(d, d.wvalid, d.wready, "W"))
        await aw
        await w
        bresp = 0
        if self.rnd:
            await ClockCycles(d.kello, self.rnd.randrange(4))
        d.bready.value = 1
        for _ in range(RAJA):
            await RisingEdge(d.kello)
            if d.bvalid.value == 1:
                bresp = int(d.bresp.value)
                break
        else:
            raise AssertionError("B: ei vastausta")
        d.bready.value = 0
        return bresp
    # @loppu kirjoita

    async def lue(self, osoite: int) -> tuple[int, int]:
        """Lukee sanan; palauttaa (data, RRESP)."""
        d = self.dut
        d.araddr.value = osoite
        await kattely(d, d.arvalid, d.arready, "AR")
        if self.rnd:
            await ClockCycles(d.kello, self.rnd.randrange(4))
        d.rready.value = 1
        for _ in range(RAJA):
            await RisingEdge(d.kello)
            if d.rvalid.value == 1:
                tulos = int(d.rdata.value), int(d.rresp.value)
                d.rready.value = 0
                return tulos
        raise AssertionError("R: ei vastausta")

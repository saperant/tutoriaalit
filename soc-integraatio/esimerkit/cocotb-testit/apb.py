"""APB-isäntä cocotb-testeihin.

APB-siirrossa on kaksi vaihetta: SETUP (PSEL) ja ACCESS (PSEL ja
PENABLE). ACCESS jatkuu, kunnes orja nostaa PREADYn; silloin siirto
päättyy ja luettu data ja PSLVERR ovat voimassa.
"""

from __future__ import annotations

from typing import Any

from cocotb.triggers import RisingEdge

RAJA = 100


class ApbIsanta:
    def __init__(self, dut: Any):
        self.dut = dut
        dut.psel.value = 0
        dut.penable.value = 0
        dut.pwrite.value = 0
        dut.pstrb.value = 0

    # @alku siirto
    async def siirto(self, osoite: int, kirjoitus: bool, data: int = 0,
                     tavut: int = 0xF) -> tuple[int, bool]:
        """Yksi APB-siirto; palauttaa (PRDATA, PSLVERR)."""
        d = self.dut
        d.paddr.value = osoite
        d.pwrite.value = kirjoitus
        d.pwdata.value = data
        d.pstrb.value = tavut if kirjoitus else 0
        d.psel.value = 1                        # SETUP
        await RisingEdge(d.kello)
        d.penable.value = 1                     # ACCESS
        for _ in range(RAJA):
            await RisingEdge(d.kello)
            if d.pready.value == 1:
                tulos = int(d.prdata.value), bool(d.pslverr.value)
                d.psel.value = 0
                d.penable.value = 0
                return tulos
        raise AssertionError(f"APB {osoite:#05x}: PREADY ei noussut")
    # @loppu siirto

    async def kirjoita(self, osoite: int, data: int, tavut: int = 0xF
                       ) -> bool:
        """Palauttaa PSLVERR:n."""
        return (await self.siirto(osoite, True, data, tavut))[1]

    async def lue(self, osoite: int) -> tuple[int, bool]:
        return await self.siirto(osoite, False)

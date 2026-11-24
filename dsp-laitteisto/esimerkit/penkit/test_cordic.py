"""CORDICin cocotb-testit: sama sarja iteratiiviselle ja
liukuhihnoitetulle toteutukselle. Ulostulot verrataan bittitarkkaan
malliin, ja tarkkuus raportoidaan liukulukuvertailuna."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import cocotb

from malli.cordic import ROTAATIO, VEKTORI, cordic
from malli.kertoimet import CORDIC_ZW, cordic_vahvistus
from virta import Ajuri, Vastaanottaja, aloita, generaattori, raportti, vertaa

KENTAT_SISAAN = ["s_tila", "s_x", "s_y", "s_z"]
KENTAT_ULOS = ["m_x", "m_y", "m_z"]
# Rotaation alkupiste 1/K muodossa Q1.15: tulos on (cos z, sin z).
X0 = round((1 << 15) / cordic_vahvistus())


def kulma16(asteet: float) -> int:
    """Asteet 16-bittiseksi kulmaksi (täysi kierros = 2**16)."""
    a = round(asteet / 360 * (1 << 16)) & 0xFFFF
    return a - (1 << 16) if a >= 1 << 15 else a


# @alku aja
async def aja(
    dut: Any, nimi: str, syotteet: Sequence[tuple[int, int, int, int]]
) -> list[tuple[int, int, int]]:
    await aloita(dut)
    rng = generaattori(nimi)
    odotettu = [cordic(*s) for s in syotteet]
    cocotb.start_soon(Ajuri(dut, KENTAT_SISAAN, rng).laheta(syotteet))
    saatu = await Vastaanottaja(dut, KENTAT_ULOS, rng).keraa(
        len(syotteet), raja=40 * len(syotteet) + 200
    )
    vertaa(nimi, [tuple(s) for s in saatu], odotettu)
    return odotettu
    # @loppu aja


# @alku tarkkuus
def virhe_lsb(arvo: int, tarkka: float, murto: int) -> float:
    """Ero tarkkaan arvoon Q-muodon LSB:inä."""
    return abs(arvo - tarkka * (1 << murto))


@cocotb.test()
async def rotaatio(dut: Any) -> None:
    """cos ja sin kulmista ympäri kierroksen (myös neljännesten rajat)."""
    kulmat = [-180, -135, -90, -45, -1, 0, 1, 30, 45, 60, 89, 90, 91,
              135, 179.99]  # fmt: skip
    rng = generaattori("rotaatio-kulmat")
    kulmat += [rng.uniform(-180, 180) for _ in range(300)]
    syotteet = [(ROTAATIO, X0, 0, kulma16(a)) for a in kulmat]
    tulos = await aja(dut, "rotaatio", syotteet)
    suurin = 0.0
    for (_, _, _, z), (x, y, _) in zip(syotteet, tulos, strict=True):
        theta = 2 * math.pi * z / (1 << 16)
        suurin = max(
            suurin,
            virhe_lsb(x, math.cos(theta), 17),
            virhe_lsb(y, math.sin(theta), 17),
        )
    raportti(f"  suurin virhe cos/sin: {suurin:.1f} LSB (Q3.17)")


@cocotb.test()
async def vektori(dut: Any) -> None:
    """atan2 ja pituus: (x, y) kierretään x-akselille."""
    rng = generaattori("vektori-pisteet")
    pisteet = [(16384, 0), (0, 16384), (-16384, 0), (0, -16384),
               (32767, 32767), (-32768, -32768),
               (1, -1), (-100, 1)]  # fmt: skip
    pisteet += [
        (rng.randint(-32768, 32767), rng.randint(-32768, 32767))
        for _ in range(300)
    ]
    syotteet = [(VEKTORI, x, y, 0) for x, y in pisteet]
    tulos = await aja(dut, "vektori", syotteet)
    k = cordic_vahvistus()
    suurin_kulma = suurin_pituus = 0.0
    for (x, y), (xo, _, zo) in zip(pisteet, tulos, strict=True):
        if abs(x) + abs(y) < 1000:
            continue  # lyhyen vektorin kulma on epätarkka
        kulma = math.atan2(y, x) / (2 * math.pi)
        ero = (zo / (1 << CORDIC_ZW) - kulma + 0.5) % 1.0 - 0.5
        suurin_kulma = max(suurin_kulma, abs(ero) * (1 << CORDIC_ZW))
        pituus = k * math.hypot(x, y) / (1 << 15)
        suurin_pituus = max(suurin_pituus, virhe_lsb(xo, pituus, 17))
    raportti(
        f"  suurin virhe kulma: {suurin_kulma:.1f} LSB (2**-18 kierrosta)"
    )
    raportti(f"  suurin virhe pituus: {suurin_pituus:.1f} LSB (Q3.17)")
    # @loppu tarkkuus

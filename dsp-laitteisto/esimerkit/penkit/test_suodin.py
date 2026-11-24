"""Suodinten cocotb-testit: sama testisarja kaikille virtaliitännän
suotimille. Ympäristömuuttuja SUODIN valitsee bittitarkan mallin
(fir, polyfaasi, sos tai cic); RTL:n valitsee ajaja (--top).

Jokainen testi syöttää näytteet satunnaisin tauoin ja vastapaineella
ja vertaa ulostuloa malliin bitilleen. Taajuusvastetesti mittaa
lisäksi vahvistuksen RTL:n ulostulosta ja vertaa sitä kertoimista
laskettuun vasteeseen toleranssilla.
"""

from __future__ import annotations

import math
import os
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

import cocotb
import numpy as np
from scipy import signal

from malli import kertoimet as k
from malli.kiintea import alue
from malli.suotimet import cic, cic_ylivuodot, desimoi, fir, sos
from virta import Ajuri, Vastaanottaja, aloita, generaattori, raportti, vertaa


# @alku asetukset
@dataclass(frozen=True)
class Suodin:
    """Mitä testit tarvitsevat suotimesta: bittitarkka malli,
    sisääntulon ja ulostulon leveys, desimointi sekä (taajuusvastetta
    varten) kertoimet b ja a liukulukuina."""

    malli: Callable[[Sequence[int], bool], list[int]]
    sisaan: int
    ulos: int
    desimointi: int = 1
    b: tuple[float, ...] = ()
    a: tuple[float, ...] = (1.0,)
    kertoimet: tuple[int, ...] = ()
    saturoi: bool = True


def _sos_ba() -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Kvantisoitujen lohkojen yhteinen siirtofunktio liukulukuina."""
    lohkot = [[c / (1 << k.IIR_MURTO) for c in s] for s in k.SOS]
    sosm = np.array(
        [[b0, b1, b2, 1.0, a1, a2] for b0, b1, b2, a1, a2 in lohkot]
    )
    b, a = signal.sos2tf(sosm)
    return tuple(float(v) for v in b), tuple(float(v) for v in a)


SUOTIMET = {
    "fir": Suodin(
        lambda x, s: fir(
            x, k.FIR, k.KERROIN_MURTO, k.DATA_BITIT, saturaatio=s
        ),
        k.DATA_BITIT,
        k.DATA_BITIT,
        b=tuple(c / (1 << k.KERROIN_MURTO) for c in k.FIR),
        kertoimet=tuple(k.FIR),
    ),
    "polyfaasi": Suodin(
        lambda x, s: desimoi(
            x, k.POLYFAASI, 4, k.KERROIN_MURTO, k.DATA_BITIT, s
        ),
        k.DATA_BITIT,
        k.DATA_BITIT,
        desimointi=4,
        kertoimet=tuple(k.POLYFAASI),
    ),
    "sos": Suodin(
        lambda x, s: sos(x, k.SOS, k.IIR_MURTO, k.IIR_BITIT, s),
        k.IIR_BITIT,
        k.IIR_BITIT,
        b=_sos_ba()[0],
        a=_sos_ba()[1],
    ),
    "cic": Suodin(
        lambda x, _: cic(
            x, k.CIC_ASTEET, k.CIC_DESIMOINTI, k.CIC_SISAINEN, k.CIC_ULOS
        ),
        k.CIC_SISAAN,
        k.CIC_ULOS,
        desimointi=k.CIC_DESIMOINTI,
        saturoi=False,
    ),
}
SUODIN = SUOTIMET[os.environ.get("SUODIN", "fir")]
# @loppu asetukset


# @alku aja
async def aja(
    dut: Any, nimi: str, x: Sequence[int], tarkista: bool = True
) -> tuple[list[int], list[int]]:
    """Syöttää x:n RTL:ään ja vertaa ulostulon malliin bitilleen.
    Palauttaa RTL:n ja mallin ulostulot; tarkista=False jättää
    vertailun kutsujalle."""
    await aloita(dut)
    rng = generaattori(nimi)
    odotettu = SUODIN.malli(x, True)
    ajuri = Ajuri(dut, ["s_data"], rng)
    vastaanottaja = Vastaanottaja(dut, ["m_data"], rng)
    cocotb.start_soon(ajuri.laheta([(v,) for v in x]))
    saatu = [
        v
        for (v,) in await vastaanottaja.keraa(
            len(odotettu), raja=40 * len(x) + 200
        )
    ]
    if tarkista:
        vertaa(nimi, saatu, odotettu, lisatieto(x, odotettu))
    return saatu, odotettu


def lisatieto(x: Sequence[int], odotettu: Sequence[int]) -> str:
    """Kertoo, kokeileeko testi rajoja. Saturoivalle suotimelle:
    moneenko näytteeseen saturaatio vaikuttaa (ero malliin, jossa
    ylivuoto kiertää). CIC:lle: monestiko integraattorit vuotavat yli."""
    if not SUODIN.saturoi:
        n = cic_ylivuodot(x, k.CIC_ASTEET, k.CIC_SISAINEN)
        return f"integraattorit vuotavat yli {n} kertaa"
    kiertava = SUODIN.malli(x, False)
    eroja = sum(a != b for a, b in zip(odotettu, kiertava, strict=True))
    return f"saturaatio vaikuttaa {eroja}"
    # @loppu aja


# @alku suunnatut
@cocotb.test()
async def impulssi(dut: Any) -> None:
    """Impulssivaste: ulostulo on kertoimet skaalattuina."""
    m = SUODIN.desimointi
    await aja(dut, "impulssi", [1 << (SUODIN.sisaan - 2)] + [0] * (24 * m))


@cocotb.test()
async def askel(dut: Any) -> None:
    """Täysi positiivinen ja negatiivinen askel: ylitys saturoituu."""
    pienin, suurin = alue(SUODIN.sisaan)
    n = 48 * SUODIN.desimointi
    await aja(dut, "askel", [suurin] * n + [pienin] * n + [0] * n)


@cocotb.test(skip=not SUOTIMET[os.environ.get("SUODIN", "fir")].kertoimet)
async def pahin(dut: Any) -> None:
    """Pahin tapaus FIR-suotimelle: jokainen näyte on täysi arvo
    kertoimen etumerkillä, jolloin summa on suurin mahdollinen."""
    pienin, suurin = alue(SUODIN.sisaan)
    h = SUODIN.kertoimet
    jakso = [suurin if c >= 0 else pienin for c in reversed(h)]
    x = (jakso * 8)[: len(jakso) * 8]
    await aja(dut, "pahin", x + [-v - 1 for v in x])
    # @loppu suunnatut


# @alku satunnainen
@cocotb.test()
async def satunnainen(dut: Any) -> None:
    """Tasajakautuneet näytteet koko alueelta."""
    rng = generaattori("satunnainen-data")
    pienin, suurin = alue(SUODIN.sisaan)
    await aja(
        dut, "satunnainen", [rng.randint(pienin, suurin) for _ in range(1600)]
    )
    # @loppu satunnainen


# @alku taajuusvaste
VALIT = 256  # mittausikkuna: taajuudet ovat sen DFT-lokeroita
LOKEROT = {"fir": (8, 32, 64, 96), "sos": (4, 13, 32, 64)}


@cocotb.test(skip=os.environ.get("SUODIN", "fir") not in LOKEROT)
async def taajuusvaste(dut: Any) -> None:
    """Vahvistus mitattuna RTL:n ulostulosta siniaalloilla.

    Jokainen taajuus on oma jaksonsa: VALIT näytettä asettumiseen ja
    VALIT mittaukseen. Taajuus osuu mittausikkunan DFT-lokeroon, joten
    amplitudi saadaan yhdestä DFT-kertoimesta ilman vuotoa."""
    lokerot = LOKEROT[os.environ.get("SUODIN", "fir")]
    amplitudi = 0.5 * (1 << (SUODIN.sisaan - 1))
    x: list[int] = []
    for kk in lokerot:
        x += [
            round(amplitudi * math.sin(2 * math.pi * kk * n / VALIT))
            for n in range(2 * VALIT)
        ]
    y, odotettu = await aja(dut, "taajuusvaste", x, tarkista=False)
    _, h = signal.freqz(
        SUODIN.b, SUODIN.a, worN=[2 * math.pi * kk / VALIT for kk in lokerot]
    )
    for i, kk in enumerate(lokerot):
        ikkuna = np.array(y[(2 * i + 1) * VALIT : (2 * i + 2) * VALIT])
        lokero = np.fft.rfft(ikkuna)[kk]
        mitattu = 2 * abs(lokero) / VALIT / amplitudi
        malli = abs(h[i])
        raportti(
            f"  f/fs = {kk / VALIT:.4f}: malli {db(malli):6.1f} dB, "
            f"RTL {db(mitattu):6.1f} dB"
        )
        assert abs(mitattu - malli) < 0.004, f"vahvistus {mitattu:.4f}"
    # Vahvistus on toleranssin sisällä; vasta bittitarkka vertailu
    # paljastaa esimerkiksi väärän pyöristyksen.
    vertaa("taajuusvaste", y, odotettu)


def db(a: float) -> float:
    return 20 * math.log10(max(a, 1e-6))
    # @loppu taajuusvaste

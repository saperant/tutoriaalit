"""NCO:n cocotb-testi: ulostulo verrataan bittitarkkaan malliin kahdella
taajuussanalla ja vastapaineella. Taajuus ja kannuspiikit lasketaan
RTL:n ulostulosta."""

from __future__ import annotations

from typing import Any

import cocotb
import numpy as np
from scipy.signal import windows

from malli.cordic import nco
from malli.kertoimet import NCO_VAIHE
from virta import Vastaanottaja, aloita, generaattori, raportti, vertaa

N = 4096


# @alku testi
async def aja(dut: Any, nimi: str, taajuussana: int) -> None:
    dut.taajuussana.value = taajuussana
    await aloita(dut)
    rng = generaattori(nimi)
    saatu = [
        v
        for (v,) in await Vastaanottaja(dut, ["m_data"], rng).keraa(
            N, raja=4 * N
        )
    ]
    vertaa(nimi, saatu, nco(taajuussana, N))
    # Spektri Blackman-Harris-ikkunalla: huippu ja suurin muu piikki.
    spektri = np.abs(np.fft.rfft(np.array(saatu) * windows.blackmanharris(N)))
    huippu = int(np.argmax(spektri))
    muut = spektri.copy()
    muut[max(0, huippu - 8) : huippu + 9] = 0
    sfdr = 20 * np.log10(spektri[huippu] / muut.max())
    raportti(
        f"  taajuus {taajuussana / (1 << NCO_VAIHE):.5f} fs, huippu "
        f"lokerossa {huippu}/{N}, SFDR {sfdr:.0f} dB"
    )


@cocotb.test()
async def tasainen(dut: Any) -> None:
    """Taajuus, jolla katkaistu vaihe toistuu: ei kannuspiikkejä."""
    await aja(dut, "tasainen", 1 << (NCO_VAIHE - 6))  # fs / 64


@cocotb.test()
async def epatasainen(dut: Any) -> None:
    """Taajuussana, jonka alimmat bitit katkaistaan: kannuspiikit."""
    await aja(dut, "epatasainen", 0x0A3D71)  # noin 0.04 fs
    # @loppu testi

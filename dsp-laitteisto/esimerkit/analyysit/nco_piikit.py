"""NCO:n kannuspiikit vaiheen katkaisun funktiona.

Käyttö: python3 analyysit/nco_piikit.py
"""

from __future__ import annotations

import math

import numpy as np
from scipy.signal import windows

from malli.cordic import nco
from malli.kertoimet import NCO_VAIHE

N = 1 << 15


# @alku sfdr
def sfdr(osoite: int, bitit: int, taajuussana: int) -> float:
    """Häiriötön dynamiikka-alue: kantoaallon ja suurimman muun piikin
    ero desibeleinä. Ikkuna vaimentaa vuodon alle -90 dB:n."""
    y = np.array(nco(taajuussana, N, NCO_VAIHE, osoite, bitit), dtype=float)
    spektri = np.abs(np.fft.rfft(y * windows.blackmanharris(N)))
    huippu = int(np.argmax(spektri))
    kantoaalto = float(spektri[huippu])
    spektri[max(0, huippu - 8) : huippu + 9] = 0  # kantoaallon lokerot
    return 20 * math.log10(kantoaalto / float(spektri.max()))


def main() -> None:
    sana = 0x0A3D71  # noin 0.04 fs; alimmat bitit eivät ole nollia
    print("vaihebitit  taulukko  SFDR (16-bittinen amplitudi)")
    for osoite in range(4, 11):
        print(
            f"{osoite + 2:10}  {1 << osoite:8}  "
            f"{sfdr(osoite, 16, sana):5.1f} dB"
        )
    print()
    print("amplitudibitit  SFDR (12 vaihebittiä)")
    for bitit in (6, 8, 10, 12, 14):
        print(f"{bitit:14}  {sfdr(10, bitit, sana):5.1f} dB")
    # @loppu sfdr


if __name__ == "__main__":
    main()

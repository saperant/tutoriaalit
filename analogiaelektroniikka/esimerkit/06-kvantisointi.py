"""Kvantisointikohina: SNR = 6,02 N + 1,76 dB simuloidulla muuntimella."""

import numpy as np
import numpy.typing as npt

from spice import lopeta, vertaa

# @alku muunnin
M, jaksot = 8192, 1021          # näytteet ja jaksojen määrä (alkuluku):
t = np.arange(M)                # koherentti näytteistys, ei ikkunaa
x = np.sin(2 * np.pi * jaksot * t / M)  # täysi alue -1...1


def muunna(x: npt.NDArray[np.float64], bitit: int) -> npt.NDArray[np.float64]:
    """Ihanteellinen N-bittinen muunnin alueelle -1...1 (keskikohta)."""
    lsb = 2 / 2**bitit
    koodi: npt.NDArray[np.float64] = np.clip(
        np.round(x / lsb - 0.5), -(2 ** (bitit - 1)), 2 ** (bitit - 1) - 1)
    tulos: npt.NDArray[np.float64] = (koodi + 0.5) * lsb
    return tulos
# @loppu muunnin


# @alku snr
for N in (6, 8, 10, 12):
    spektri = np.abs(np.fft.rfft(muunna(x, N))) ** 2
    signaali = spektri[jaksot]
    kohina = spektri[1:].sum() - signaali     # tasakomponentti pois
    snr = 10 * np.log10(signaali / kohina)
    vertaa(f"N = {N}", float(snr), 6.02 * N + 1.76, "dB", 0.01)
# @loppu snr
lopeta()

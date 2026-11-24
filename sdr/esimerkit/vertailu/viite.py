"""C++-ketjun Python-vastine: sama NCO-taulukko, suodin ja ilmaisin."""

import numpy as np
from numpy.typing import NDArray
from scipy import signal

Reaali = NDArray[np.float64]
Kompleksi = NDArray[np.complex128]


# @alku viite
def ketju(z: Kompleksi, kanava_hz: float, fs: float = 912e3,
          desimointi: int = 4, poikkeama: float = 75e3) -> Reaali:
    """Kuten main.cpp:n Ketju, mutta koko tallenne kerralla."""
    askel = round(kanava_hz / fs * 2**32) & 0xFFFFFFFF
    vaihe = (np.arange(len(z), dtype=np.uint64) * askel) & 0xFFFFFFFF
    taulukko = np.exp(-2j * np.pi * np.arange(4096) / 4096)
    sekoitettu = z * taulukko[vaihe >> 20]
    h = signal.firwin(129, 100e3, fs=fs)
    y = signal.upfirdn(h, sekoitettu, down=desimointi)
    y = y[:(len(z) + desimointi - 1) // desimointi]   # vain hannan alku
    m: Reaali = np.angle(y[1:] * np.conj(y[:-1])) * (fs / desimointi) / (
        2 * np.pi * poikkeama)
    return m
# @loppu viite

"""Pieni suodinkirjasto: liukuva keskiarvo, EMA ja lovisuodin."""

from __future__ import annotations

import numpy as np
import numpy.typing as npt
from scipy import signal

Jono = npt.NDArray[np.float64]


# @alku keskiarvo
def liukuva_keskiarvo(x: Jono, M: int) -> Jono:
    """Kausaalinen M näytteen keskiarvo, nollatila alussa."""
    if M < 1:
        raise ValueError(f"ikkunan pituus {M} < 1")
    return np.convolve(x, np.full(M, 1.0 / M))[:len(x)]
# @loppu keskiarvo


# @alku ema
class Eksponentiaalinen:
    """y[n] = y[n-1] + alfa (x[n] - y[n-1]); tila säilyy kutsujen välillä."""

    def __init__(self, alfa: float) -> None:
        if not 0.0 < alfa <= 1.0:
            raise ValueError(f"alfa {alfa} ei ole välillä (0, 1]")
        self.b = np.array([alfa])
        self.a = np.array([1.0, alfa - 1.0])
        self.tila = np.zeros(1)

    def kasittele(self, lohko: Jono) -> Jono:
        y, self.tila = signal.lfilter(self.b, self.a, lohko, zi=self.tila)
        return np.asarray(y, dtype=np.float64)
# @loppu ema


# @alku lovi
def lovi(f0: float, fs: float, r: float = 0.98) -> tuple[Jono, Jono]:
    """Nollat yksikköympyrällä taajuudella f0, navat säteellä r.

    Vahvistus on normitettu ykköseksi tasajännitteellä.
    """
    if not 0.0 < f0 < fs / 2:
        raise ValueError(f"f0 = {f0} Hz ei ole välillä (0, fs/2)")
    if not 0.0 < r < 1.0:
        raise ValueError(f"napojen säde {r} ei ole välillä (0, 1)")
    w0 = 2 * np.pi * f0 / fs
    b = np.array([1.0, -2 * np.cos(w0), 1.0])
    a = np.array([1.0, -2 * r * np.cos(w0), r**2])
    return b * np.sum(a) / np.sum(b), a
# @loppu lovi


def vahvistus_db(b: Jono, a: Jono, f: float, fs: float) -> float:
    """Taajuusvasteen itseisarvo desibeleinä taajuudella f."""
    _, H = signal.freqz(b, a, worN=[f], fs=fs)
    return float(20 * np.log10(abs(H[0])))

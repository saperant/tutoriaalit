"""Virtaava käsittely lohkoittain: overlap-add ja tilan säilyttäminen."""

import numpy as np
import numpy.typing as npt
from scipy import signal

Jono = npt.NDArray[np.float64]


# @alku overlap-add
class LohkoFIR:
    """FIR-suodin, joka ottaa syötteen paloina ja palauttaa paloja."""

    def __init__(self, h: Jono) -> None:
        self.h = h
        self.hanta = np.zeros(len(h) - 1)    # edellisen lohkon jälki

    def kasittele(self, lohko: Jono) -> Jono:
        y = np.convolve(lohko, self.h)        # pituus L + M - 1
        y[:len(self.hanta)] += self.hanta
        self.hanta = y[len(lohko):].copy()
        return y[:len(lohko)]
# @loppu overlap-add


# @alku vertailu
rng = np.random.default_rng(11)
x = rng.normal(size=1_000)
h = signal.firwin(31, 0.2)                    # alipäästö-FIR, 31 kerrointa
kokonaan = np.convolve(x, h)[:len(x)]

suodin = LohkoFIR(h)
palat = [suodin.kasittele(x[i:i + 128]) for i in range(0, len(x), 128)]
print("overlap-add == kokonaan:", bool(np.allclose(np.concatenate(palat),
                                                    kokonaan)))

# Sama scipyllä: lfilter palauttaa ja ottaa suotimen tilan zi.
tila = np.zeros(len(h) - 1)
palat2 = []
for i in range(0, len(x), 100):
    y, tila = signal.lfilter(h, [1.0], x[i:i + 100], zi=tila)
    palat2.append(y)
print("lfilter + zi == kokonaan:", bool(np.allclose(np.concatenate(palat2),
                                                     kokonaan)))

# Virhe: tila unohtuu lohkojen välillä.
palat3 = [np.convolve(x[i:i + 128], h)[:128] for i in range(0, len(x), 128)]
virhe = np.abs(np.concatenate(palat3)[:len(x)] - kokonaan)
vaarat = np.flatnonzero(virhe > 1e-9)
print(f"ilman tilaa: suurin virhe {np.max(virhe):.2f},"
      f" virheet vain {len(h) - 1} ensimmäisessä:",
      bool(np.all(vaarat % 128 < len(h) - 1)))
# @loppu vertailu

"""Python-referenssit, joihin C-toteutuksia verrataan."""

import numpy as np
from numpy.typing import NDArray


# @alku vertaa
def suhteellinen_ero(saatu: NDArray[np.float64] | NDArray[np.complex128],
                     viite: NDArray[np.float64] | NDArray[np.complex128]
                     ) -> float:
    """Suurin ero suhteessa viitteen suurimpaan itseisarvoon.

    Normitus signaalin tasoon eika kuhunkin naytteeseen: nollan
    lahella olevat naytteet eivat rajahda suhteellisina virheina."""
    if saatu.shape != viite.shape:
        raise ValueError(f"muodot eroavat: {saatu.shape} != {viite.shape}")
    taso = float(np.max(np.abs(viite)))
    return float(np.max(np.abs(saatu - viite))) / (taso or 1.0)
# @loppu vertaa


# @alku nlms
def nlms(x: NDArray[np.float64], d: NDArray[np.float64], lkm: int,
         mu: float, eps: float = 1e-8) -> NDArray[np.float64]:
    """NLMS suoraan kaavasta: energia lasketaan joka askeleella."""
    w = np.zeros(lkm)
    v = np.zeros(lkm)
    e = np.empty(x.size)
    for n in range(x.size):
        v = np.roll(v, 1)
        v[0] = x[n]
        e[n] = d[n] - w @ v
        w += mu * e[n] / (eps + v @ v) * v
    return e
# @loppu nlms


# @alku q15
def q15_prosessori(h: NDArray[np.int16], x: NDArray[np.int16],
                   vahvistus: int) -> tuple[NDArray[np.int16], int]:
    """Bittitarkka malli: kokonaisluvut, pyoristys ja saturaatio."""
    kertyma = np.convolve(x.astype(np.int64), h.astype(np.int64))[:x.size]
    suodatettu = np.clip((kertyma + (1 << 14)) >> 15, -32768, 32767)
    tulos = (suodatettu * vahvistus + (1 << 11)) >> 12
    ulos = np.clip(tulos, -32768, 32767)
    return ulos.astype(np.int16), int(np.count_nonzero(ulos != tulos))
# @loppu q15

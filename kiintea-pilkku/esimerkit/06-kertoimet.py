"""Kertoimien kvantisointi: FIR-suodattimen estokaistan vaimennus
riippuu kerroinbittien määrästä."""

import numpy as np
import numpy.typing as npt

Liuku = npt.NDArray[np.float64]


# @alku suunnittelu
def alipaasto(pituus: int, raja: float) -> Liuku:
    """Ikkunoitu sinc-alipäästö (Hamming); raja suhteessa fs:ään."""
    n = np.arange(pituus) - (pituus - 1) / 2
    h = 2 * raja * np.sinc(2 * raja * n) * np.hamming(pituus)
    return np.asarray(h / h.sum(), dtype=np.float64)   # vahvistus 1


def estokaista_db(h: Liuku, alku: float) -> float:
    """Pahin (suurin) vaste estokaistalla [alku, 0,5] desibeleinä."""
    vaste = np.abs(np.fft.rfft(h, 1 << 14))
    f = np.fft.rfftfreq(1 << 14)
    return float(20 * np.log10(np.max(vaste[f >= alku])))
# @loppu suunnittelu


def kvantisoi(h: Liuku, bitit: int) -> Liuku:
    skaala = float(1 << (bitit - 1))
    return np.asarray(np.round(h * skaala) / skaala, dtype=np.float64)


# @alku mittaus
h = alipaasto(41, 0.1)
print(f"{'kertoimet':>10} {'estokaista (dB)':>16}")
print(f"{'double':>10} {estokaista_db(h, 0.15):>16.1f}")
for bitit in (16, 12, 10, 8, 6):
    hq = kvantisoi(h, bitit)
    print(f"{bitit:>7} b. {estokaista_db(hq, 0.15):>16.1f}")
# @loppu mittaus

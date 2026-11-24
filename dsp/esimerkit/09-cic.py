"""CIC-desimoija kokonaisluvuilla: ylivuoto ei haittaa."""

import numpy as np

R, N = 8, 3                                 # harvennus ja asteiden maara


# @alku cic
def cic(x: np.ndarray, sanaleveys: int) -> np.ndarray:
    """N integraattoria, harvennus R, N kampaa. Kaksi komplementti
    -aritmetiikka sanaleveydessa: ylivuodot kumoutuvat kammoissa."""
    maski = (1 << sanaleveys) - 1

    def kaari(v: np.ndarray) -> np.ndarray:  # tulkinta etumerkillisena
        v = v & maski
        return np.where(v >= 1 << (sanaleveys - 1), v - (1 << sanaleveys), v)

    v = x.astype(np.int64)
    for _ in range(N):                      # integraattorit, tahti fs
        v = kaari(np.cumsum(v))
    v = v[R - 1::R]                         # harvennus
    for _ in range(N):                      # kammat, tahti fs / R
        v = kaari(v - np.concatenate([[0], v[:-1]]))
    return v
# @loppu cic


# @alku vertaa
rng = np.random.default_rng(11)
x = rng.integers(-2**11, 2**11, 4_000)      # 12-bittinen syote
x[:200] = -2**11                            # pahin tapaus: taysi tasajannite
leveys = 12 + N * int(np.log2(R))           # Hogenauer: B + N log2 R
laatikko = np.ones(R, dtype=np.int64)       # liukuva summa R naytetta
ydin = np.convolve(np.convolve(laatikko, laatikko), laatikko)
viite = np.convolve(x, ydin)[:x.size][R - 1::R]
for bitit in (leveys, leveys - 1):
    tulos = cic(x, bitit)
    print(f"{bitit} bittia: sama kuin (laatikko*3)-konvoluutio:"
          f" {np.array_equal(tulos, viite)}")
print(f"tasavahvistus R^N = {R**N}, integraattori ylivuoti:"
      f" {np.abs(np.cumsum(np.cumsum(x))).max() > 2**(leveys - 1)}")
# @loppu vertaa

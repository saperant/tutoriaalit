"""BPSK Rayleigh-häipymässä ja kahden antennin diversiteetillä."""

import math

import numpy as np
from scipy.special import erfc

rng = np.random.default_rng(10)


def kompleksi_normaali(*koko: int) -> np.ndarray:
    """CN(0, 1): kompleksinen normaalijakauma, teho 1."""
    z: np.ndarray = (rng.standard_normal(koko)
                     + 1j * rng.standard_normal(koko)) / np.sqrt(2)
    return z


# @alku teoria
def rayleigh(g: float, L: int) -> float:
    """BPSK:n BER, L haaraa ja suhdeyhdistely (MRC), keskim. Eb/N0 = g."""
    mu = np.sqrt(g / (1 + g))
    summa = sum(math.comb(L - 1 + k, k) * ((1 + mu) / 2) ** k
                for k in range(L))
    return float(((1 - mu) / 2) ** L * summa)
# @loppu teoria


# @alku simuloi
n = 2_000_000
bitit = rng.integers(0, 2, n)
s = 1.0 - 2 * bitit
print("Eb/N0   AWGN       Rayleigh: sim / teoria    2 antennia: sim / teoria")
for EbN0_dB in (10.0, 20.0):
    g = 10 ** (EbN0_dB / 10)
    awgn = 0.5 * erfc(np.sqrt(g))
    tulokset = []
    for L in (1, 2):
        h = kompleksi_normaali(L, n)           # kanavan kerroin per haara
        r = h * s + kompleksi_normaali(L, n) / np.sqrt(g)   # N0 = 1/g
        # MRC: painot conj(h), haarat summataan. Tunnettu kanava.
        paatos = np.sum(np.conj(h) * r, axis=0).real < 0
        tulokset.append((np.mean(paatos != bitit), rayleigh(g, L)))
    (s1, t1), (s2, t2) = tulokset
    print(f"{EbN0_dB:4.0f} dB {awgn:9.2e}   {s1:9.2e} / {t1:9.2e}"
          f"     {s2:9.2e} / {t2:9.2e}")
# @loppu simuloi

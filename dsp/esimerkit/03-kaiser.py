"""Kaiserin ikkunan parametrit kaavoista ja suunnittelu vaatimuksiin."""

import math

import numpy as np
from scipy import signal


# @alku kaavat
def kaiser_beta(A: float) -> float:
    """Kaiserin beta vaimennuksesta A (dB)."""
    if A > 50:
        return 0.1102 * (A - 8.7)
    if A >= 21:
        return 0.5842 * math.pow(A - 21, 0.4) + 0.07886 * (A - 21)
    return 0.0


def kaiser_pituus(A: float, siirtyma: float) -> int:
    """Kertoimien maara; siirtyma suhteessa naytetaajuuteen (f/fs)."""
    return math.ceil((A - 7.95) / (2.285 * 2 * math.pi * siirtyma)) + 1
# @loppu kaavat


# @alku vertaa
A, fs = 70.0, 48_000.0
paasto, esto = 4_000.0, 5_000.0
lkm = kaiser_pituus(A, (esto - paasto) / fs)
oma = (lkm, kaiser_beta(A))
scipy_arvo = signal.kaiserord(A, (esto - paasto) / (fs / 2))
print(f"kaavat: N = {oma[0]}, beta = {oma[1]:.4f}")
print(f"kaiserord: N = {scipy_arvo[0]}, beta = {scipy_arvo[1]:.4f}")
# @loppu vertaa


# @alku iteroi
def vaimennus(h: np.ndarray) -> float:
    f, H = signal.freqz(h, worN=1 << 15, fs=fs)
    return float(-20 * np.log10(np.abs(H[f >= esto]).max()))


lkm = oma[0] | 1                     # pariton: tyyppi I, viive kokonaisluku
while True:
    h = signal.firwin(lkm, (paasto + esto) / 2,
                      window=("kaiser", kaiser_beta(A)), fs=fs)
    saatu = vaimennus(h)
    print(f"N = {lkm}: vaimennus {saatu:.2f} dB")
    if saatu >= A:
        break
    lkm += 2
# @loppu iteroi

"""Biquadin kertoimien kvantisointi Q2.14- ja Q2.30-muotoon."""

import numpy as np
from scipy import signal

fs = 48_000.0


# @alku kvantisoi
def kvantisoi(c: np.ndarray, bitit: int) -> np.ndarray:
    """Pyoristys murto-osan bitteihin (Q2.bitit, koska |a1| < 2)."""
    q: np.ndarray = np.round(c * 2**bitit) / 2**bitit
    return q
# @loppu kvantisoi


# @alku vertaa
def kuvaus(b: np.ndarray, a: np.ndarray) -> str:
    if not b.any():
        return "b pyoristyi nollaksi"
    f, H = signal.freqz(b, a, worN=1 << 18, fs=fs)
    amp = np.abs(H)
    raja = f[np.argmax(amp < amp[0] / 2**0.5)]
    dc = round(20 * float(np.log10(amp[0])), 2) + 0.0     # ei miinusnollaa
    return f"DC {dc:6.2f} dB, -3 dB {raja:7.1f} Hz"


for fc in (50.0, 500.0, 5_000.0):
    b, a = signal.butter(2, fc, fs=fs)
    napa = np.abs(np.roots(a))[0]
    print(f"{fc:4.0f} Hz: b0 = {b[0]:.2e}, |napa| {napa:.5f}")
    for bitit in (14, 30):
        bq, aq = kvantisoi(b, bitit), kvantisoi(a, bitit)
        print(f"  Q2.{bitit}: {kuvaus(bq, aq)}")
# @loppu vertaa

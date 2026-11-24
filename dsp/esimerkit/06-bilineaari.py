"""Bilineaarimuunnos: taajuusakselin vaaristyminen ja esivaaristys."""

import math

import numpy as np
from scipy import signal

fs = 48_000.0


# @alku muunnos
def rc_alipaasto(fc: float, esivaarista: bool) -> tuple[np.ndarray,
                                                         np.ndarray]:
    """Analoginen H(s) = 1 / (1 + s / wc) digitaaliseksi."""
    wc = 2 * math.pi * fc
    if esivaarista:
        # Valitaan analoginen raja niin, etta se kuvautuu tasan fc:hen.
        wc = 2 * fs * math.tan(math.pi * fc / fs)
    b, a = signal.bilinear([1.0], [1.0 / wc, 1.0], fs=fs)
    return b, a
# @loppu muunnos


# @alku mittaa
def raja_3db(b: np.ndarray, a: np.ndarray) -> float:
    f, H = signal.freqz(b, a, worN=1 << 18, fs=fs)
    return float(f[np.argmax(np.abs(H) < 1 / math.sqrt(2))])


print(" haluttu    ilman     esivaaristys")
for fc in (100.0, 1_000.0, 5_000.0, 15_000.0):
    ilman = raja_3db(*rc_alipaasto(fc, False))
    kanssa = raja_3db(*rc_alipaasto(fc, True))
    print(f"{fc:8.0f} {ilman:8.0f} Hz {kanssa:8.0f} Hz")
# @loppu mittaa

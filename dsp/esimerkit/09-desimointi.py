"""Desimointi: harvennus ilman suodatinta laskostaa, suodatus estaa."""

import numpy as np
from scipy import signal

fs, M = 48_000.0, 4                         # 48 kHz -> 12 kHz
n = np.arange(48_000)
x = np.sin(2 * np.pi * 1_000.0 / fs * n) + 0.5 * np.sin(
    2 * np.pi * 7_000.0 / fs * n)           # 7 kHz > uusi Nyquist 6 kHz


# @alku taso
def taso_db(y: np.ndarray, f: float, fs_y: float) -> float:
    """Sinin amplitudi taajuudella f (dB suhteessa amplitudiin 1)."""
    k = np.exp(-2j * np.pi * f / fs_y * np.arange(y.size))
    db = 20 * np.log10(2 * abs(np.mean(y * k)) + 1e-12)
    return round(float(db), 1) + 0.0         # ei miinusnollaa
# @loppu taso


# @alku vertaa
h = signal.firwin(97, 5_000.0, window=("kaiser", 8.0), fs=fs)
suoraan = x[::M]
suodatettu = signal.lfilter(h, [1.0], x)[::M]
for nimi, y in (("ilman suodinta", suoraan), ("FIR ensin", suodatettu)):
    y = y[-6_000:]                          # 0,5 s, transientti ohi
    print(f"{nimi:15s} 1 kHz {taso_db(y, 1_000.0, fs / M):6.1f} dB,"
          f" laskos 5 kHz {taso_db(y, 5_000.0, fs / M):6.1f} dB")
# @loppu vertaa

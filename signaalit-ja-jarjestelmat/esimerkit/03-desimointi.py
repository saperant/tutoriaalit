"""Näytetaajuuden pienentäminen: joka neljäs näyte vai suodatus ensin."""

import numpy as np
from scipy import signal

# @alku desimointi
fs = 8_000.0
t = np.arange(8_000) / fs
hyotysignaali = np.sin(2 * np.pi * 300 * t)
hairio = 0.5 * np.sin(2 * np.pi * 2_700 * t)    # yli uuden Nyquistin
x = hyotysignaali + hairio

q = 4                                           # uusi fs = 2000 Hz
suora = x[::q]
suodatettu = signal.decimate(x, q, ftype="fir", zero_phase=True)


def amplitudi(y: np.ndarray, f: float, fs_uusi: float) -> float:
    """Taajuuden f amplitudi korrelaatiolla (kokonaiset jaksot)."""
    n = np.arange(len(y))
    return float(2 * np.abs(np.mean(y * np.exp(-2j * np.pi * f / fs_uusi
                                                * n))))


fs_uusi = fs / q
alias = 2_700 - fs_uusi                         # 2700 Hz -> 700 Hz
for nimi, y in (("joka 4. näyte", suora), ("decimate", suodatettu)):
    print(f"{nimi:<14} 300 Hz: {amplitudi(y, 300, fs_uusi):.3f},"
          f" alias {alias:.0f} Hz: {amplitudi(y, alias, fs_uusi):.3f}")
# @loppu desimointi

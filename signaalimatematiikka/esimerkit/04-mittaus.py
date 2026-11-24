"""Osoittimen mittaus näytteistä korrelaatiolla."""

import cmath
import math

import numpy as np
from numpy.typing import NDArray

Taulukko = NDArray[np.float64]


def napa(z: complex) -> str:
    """Osoitin muodossa A kulma phi (asteina)."""
    kulma = round(math.degrees(cmath.phase(z)), 2) + 0.0
    return f"{abs(z):.3f} kulmassa {kulma:.2f} astetta"


# @alku mittaus
def mittaa_osoitin(x: Taulukko, f: float, fs: float) -> complex:
    """Korrelaatio kompleksiseen eksponenttiin, x kokonaisia jaksoja."""
    n = np.arange(len(x))
    return complex(2 * np.mean(x * np.exp(-2j * np.pi * f * n / fs)))


fs = 8000.0
n = np.arange(160)                      # 20 ms = 5 jaksoa 250 Hz:llä
signaali = (2.0 * np.cos(2 * np.pi * 250 * n / fs + 1.0)
            + 0.7 * np.cos(2 * np.pi * 750 * n / fs - 0.4))
for taajuus in [250.0, 500.0, 750.0]:
    Xm = mittaa_osoitin(signaali, taajuus, fs)
    kuvaus = napa(Xm) if abs(Xm) > 1e-9 else "ei komponenttia"
    print(f"{taajuus:5.0f} Hz: {kuvaus}")
# @loppu mittaus

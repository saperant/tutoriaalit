"""Tehollisarvo numeerisesti verrattuna kaavoihin."""

import math

import numpy as np

# @alku rms
t = np.linspace(0, 1, 100_000, endpoint=False)   # yksi jakso, f = 1 Hz
huippu = 325.0                                   # verkkojännitteen huippu
muodot = {
    "sini": huippu * np.sin(2 * np.pi * t),
    "kanttiaalto": huippu * np.sign(np.sin(2 * np.pi * t)),
    "kolmio": huippu * (4 * np.abs(t - np.floor(t + 0.5)) - 1),
}
kaavat = {"sini": huippu / math.sqrt(2), "kanttiaalto": huippu,
          "kolmio": huippu / math.sqrt(3)}
for nimi, u in muodot.items():
    rms = float(np.sqrt(np.mean(u**2)))    # neliöiden keskiarvon neliöjuuri
    print(f"{nimi:<12} numeerinen {rms:7.2f} V, kaava {kaavat[nimi]:7.2f} V")
# @loppu rms

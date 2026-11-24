"""Amplitudin kvantisointi: mitattu SNR vs. 6.02 b + 1.76 dB."""

import numpy as np

# @alku kvantisointi
n = np.arange(100_000)
x = 0.999 * np.sin(2 * np.pi * 0.01234 * n)   # lähes täysi asteikko
for bitit in (8, 12, 16):
    askel = 2.0 / 2**bitit                    # alue [-1, 1)
    xq = np.round(x / askel) * askel
    kohina = xq - x
    snr = 10 * np.log10(np.mean(x**2) / np.mean(kohina**2))
    print(f"{bitit:2d} bittiä: SNR {snr:5.1f} dB,"
          f" kaava {6.02 * bitit + 1.76:5.1f} dB")
# @loppu kvantisointi

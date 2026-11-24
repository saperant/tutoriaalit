"""Goertzelin algoritmi: yhden taajuuden DFT-arvo, esim. DTMF-tunnistus."""

import math

import numpy as np


# @alku goertzel
def goertzel(x: np.ndarray, k: int) -> complex:
    """DFT:n arvo X[k] toisen asteen resonaattorilla: 1 kertolasku/nayte."""
    w = 2 * math.pi * k / x.size
    c = 2 * math.cos(w)
    s1 = s2 = 0.0
    for xn in x:
        s1, s2 = float(xn) + c * s1 - s2, s1
    # Viimeinen askel antaa kompleksisen arvon (vaihe mukaan lukien).
    return complex(s1 - math.cos(w) * s2, math.sin(w) * s2) * complex(
        math.cos(w * (x.size - 1)), -math.sin(w * (x.size - 1)))
# @loppu goertzel


# @alku dtmf
fs, N = 8_000.0, 205                        # DTMF-standardin tyypillinen N
rivit = [697.0, 770.0, 852.0, 941.0]
sarakkeet = [1_209.0, 1_336.0, 1_477.0]
nappaimet = ["123", "456", "789", "*0#"]
n = np.arange(N)
for rivi, sarake in ((1, 2), (3, 1)):
    x = (np.sin(2 * math.pi * rivit[rivi] / fs * n)
         + np.sin(2 * math.pi * sarakkeet[sarake] / fs * n))
    tasot = [abs(goertzel(x, round(f * N / fs))) for f in rivit + sarakkeet]
    r = int(np.argmax(tasot[:4]))
    s = int(np.argmax(tasot[4:]))
    print(f"tunnistettu {nappaimet[r][s]}, tasot "
          + " ".join(f"{t:5.1f}" for t in tasot))
X = np.fft.fft(x)
k = round(sarakkeet[1] * N / fs)
print(f"vertailu FFT:hen bin {k}: ero alle 1e-9: "
      f"{abs(goertzel(x, k) - X[k]) < 1e-9}")
# @loppu dtmf

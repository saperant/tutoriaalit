"""AM: modulaatioaste, verhokäyräilmaisu ja koherentti ilmaisu."""

import numpy as np
from scipy import signal

fs, fc = 200_000.0, 20_000.0
t = np.arange(40_000) / fs
viesti = 0.7 * np.cos(2 * np.pi * 300 * t) + 0.3 * np.sin(2 * np.pi * 800 * t)
alipaasto = signal.butter(4, 2_000.0, fs=fs, output="sos")
keski = slice(4_000, -4_000)


def saro(y: np.ndarray) -> float:
    """Särö prosentteina: se osa ilmaistusta, joka ei ole viestin muotoa.

    Tasakomponentti ja vahvistus eivät ole säröä, joten ne sovitetaan pois.
    """
    a, b = y[keski] - y[keski].mean(), viesti[keski] - viesti[keski].mean()
    rho = np.dot(a, b) / np.sqrt(np.dot(a, a) * np.dot(b, b))
    return float(100 * np.sqrt(max(1 - rho**2, 0.0)))


# @alku ilmaisimet
def verhokayra(s: np.ndarray) -> np.ndarray:
    """Diodi ja RC-suodin: tasasuuntaus ja alipäästö."""
    return signal.sosfiltfilt(alipaasto, np.abs(s))


def koherentti(s: np.ndarray, vaihe: float) -> np.ndarray:
    """Kerrotaan paikallisella kantoaallolla ja suodatetaan 2 fc pois."""
    lo = 2 * np.cos(2 * np.pi * fc * t + vaihe)
    return signal.sosfiltfilt(alipaasto, s * lo)
# @loppu ilmaisimet


# @alku aste
for mu in (0.5, 1.0, 1.5):
    s = (1 + mu * viesti) * np.cos(2 * np.pi * fc * t)
    hyotysuhde = mu**2 * np.mean(viesti**2) / (1 + mu**2 * np.mean(viesti**2))
    print(f"mu = {mu:.1f}: särö: verhokäyrä {saro(verhokayra(s)):4.1f} %,"
          f" koherentti {saro(koherentti(s, 0.0)):4.1f} %,"
          f" viestin teho {100 * hyotysuhde:2.0f} %")
# @loppu aste

# @alku vaihe
dsb = viesti * np.cos(2 * np.pi * fc * t)     # DSB-SC: ei kantoaaltoa
for asteet in (0, 30, 60, 90):
    y = koherentti(dsb, np.radians(asteet))
    vahvistus = np.std(y[keski]) / np.std(viesti[keski])
    print(f"DSB-SC, vaihevirhe {asteet:2d} astetta:"
          f" vahvistus {vahvistus:.3f}")
# @loppu vaihe

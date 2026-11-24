"""Aliasointi: eri taajuudet, samat näytteet."""

import numpy as np
import numpy.typing as npt


def jono(x: npt.NDArray[np.float64]) -> str:
    return " ".join(f"{v:5.2f}" for v in np.round(x, 2) + 0.0)


# @alku laskos
def nakyva_taajuus(f: float, fs: float) -> float:
    """Taajuus, jolta näytteistetty sini näyttää, väliltä [0, fs/2]."""
    jaannos = f % fs                      # siirto fs:n monikerroilla
    return min(jaannos, fs - jaannos)     # peilaus Nyquistin ympäri


fs = 10_000.0
for f in (3_000.0, 7_000.0, 13_000.0, 10_000.0, 5_000.0, 24_400.0):
    print(f"{f:7.0f} Hz -> näkyy {nakyva_taajuus(f, fs):5.0f} Hz")
# @loppu laskos

# @alku samat
t = np.arange(8) / fs
a = np.cos(2 * np.pi * 3_000 * t)
b = np.cos(2 * np.pi * 7_000 * t)
c = np.sin(2 * np.pi * 7_000 * t)
print("cos 3 kHz:", jono(a))
print("cos 7 kHz:", jono(b))
print("sin 7 kHz:", jono(c))
print("cos samat:", bool(np.allclose(a, b)))
print("sin 7 kHz = -sin 3 kHz:",
      bool(np.allclose(c, -np.sin(2 * np.pi * 3_000 * t))))
# @loppu samat

# @alku spektri
# Spektri ei paljasta, kumpi taajuus oli alkuperäinen.
N = 1000
t = np.arange(N) / fs
for f in (3_000.0, 7_000.0, 13_000.0):
    X = np.fft.rfft(np.cos(2 * np.pi * f * t))
    taajuudet = np.fft.rfftfreq(N, d=1 / fs)
    huippu = taajuudet[np.argmax(np.abs(X))]
    print(f"näytteistetty {f:6.0f} Hz: spektrin huippu {huippu:5.0f} Hz")
# @loppu spektri

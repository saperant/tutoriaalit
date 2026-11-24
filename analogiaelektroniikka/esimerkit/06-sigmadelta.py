"""Ensimmäisen kertaluvun sigma-delta-modulaattori: kohinanmuokkaus.

Yksibittinen kvantisointi tuottaa valtavasti kohinaa, mutta takaisin-
kytketty integraattori siirtää sen korkeille taajuuksille. Kaistan
kohina pienenee noin 9 dB jokaista ylinäytteistyksen kaksinkertaistusta
kohden (3 dB tavallinen ylinäytteistys + 6 dB muokkaus).
"""

import numpy as np
import numpy.typing as npt

from spice import lopeta, vertaa

# @alku modulaattori
M = 2**16
jaksot = 31                                   # signaalin taajuus fs * 31/M
x = 0.5 * np.sin(2 * np.pi * jaksot * np.arange(M) / M)
# Pieni lisäkohina (dither) vertailijan tulossa hajottaa ensimmäisen
# kertaluvun modulaattorin jaksolliset kuviot, jotka muuten näkyvät
# kaistalla piikkeinä. Se muokkautuu kuten kvantisointikohina.
dither = np.random.default_rng(1).uniform(-0.5, 0.5, M)


def modulaattori(x: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    """Integraattori summaa tulon ja lähdön erotuksen; vertailija antaa
    +1 tai -1. Lähdön keskiarvo seuraa tuloa."""
    v = np.empty_like(x)
    integraali, y = 0.0, 0.0
    for n, xn in enumerate(x):
        integraali += xn - y
        y = 1.0 if integraali + dither[n] >= 0 else -1.0
        v[n] = y
    return v
# @loppu modulaattori


# @alku kaista
bitit = modulaattori(x)
spektri = np.abs(np.fft.rfft(bitit)) ** 2
edellinen = None
for osr in (16, 32, 64, 128):
    kaista = M // (2 * osr)                   # kaistan reuna FFT-lokeroina
    signaali = spektri[jaksot]
    kohina = spektri[1:kaista].sum() - signaali
    snr = float(10 * np.log10(signaali / kohina))
    print(f"OSR {osr:3d}: SNR kaistalla {snr:5.1f} dB")
    if edellinen is not None:
        vertaa("parannus", snr - edellinen, 9.0, "dB", 0.2)
    edellinen = snr
# @loppu kaista
lopeta()

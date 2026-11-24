"""Automaattinen vahvistuksen saato (AGC): nopea isku, hidas palautus."""

import numpy as np

fs = 48e3
rng = np.random.default_rng(9)
# @alku tulo
# Signaalin taso muuttuu: -40 dBFS, sitten -10 dBFS (lahelle tullut
# lahetin) ja lopuksi -25 dBFS. Kukin jakso 0,1 s.
tasot_db = np.repeat([-40.0, -10.0, -25.0], round(0.1 * fs))
k = np.arange(len(tasot_db))
x = 10 ** (tasot_db / 20) * np.exp(2j * np.pi * 1e3 * k / fs)
x += 1e-4 * (rng.standard_normal(len(k)) + 1j * rng.standard_normal(len(k)))
# @loppu tulo


# @alku agc
def agc(z: np.ndarray, tavoite_db: float = -6.0, isku_ms: float = 1.0,
        palautus_ms: float = 50.0) -> np.ndarray:
    """Tehon verhokayra dB-asteikolla; vahvistus seuraa nopeasti ylos-
    pain (isku, ettei ylikuormitu) ja hitaasti alaspain (palautus)."""
    a_isku = 1 - np.exp(-1 / (isku_ms * 1e-3 * fs))
    a_palautus = 1 - np.exp(-1 / (palautus_ms * 1e-3 * fs))
    taso = tavoite_db
    y = np.empty_like(z)
    for i, nayte in enumerate(z):
        hetki = 20 * np.log10(abs(nayte) + 1e-12)
        a = a_isku if hetki > taso else a_palautus
        taso += a * (hetki - taso)
        y[i] = nayte * 10 ** ((tavoite_db - taso) / 20)
    return y
# @loppu agc


# @alku ajo
y = agc(x)
for alku_ms in (0, 20, 95, 100, 101, 105, 195, 200, 230, 280):
    i = round(alku_ms * 1e-3 * fs)
    osa = y[i:i + 48]                         # 1 ms:n keskiarvo
    taso = 10 * np.log10(np.mean(np.abs(osa) ** 2))
    print(f"{alku_ms:4} ms: tulo {tasot_db[i]:4.0f} dBFS, lahto {taso:6.1f} "
          "dBFS")
# @loppu ajo

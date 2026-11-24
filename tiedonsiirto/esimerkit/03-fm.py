"""FM: modulaatioindeksi, Carsonin sääntö ja demodulointi vaihe-erolla."""

import numpy as np
from scipy import signal
from scipy.special import jv

# @alku moduloi
fs = 200_000.0
t = np.arange(200_000) / fs                   # 1 s: 1 Hz:n resoluutio
fm, df = 1_000.0, 5_000.0                     # viestin taajuus ja poikkeama
viesti = np.cos(2 * np.pi * fm * t)
vaihe = 2 * np.pi * df * np.cumsum(viesti) / fs   # taajuuden integraali
kanta = np.exp(1j * vaihe)                    # kantataajuinen FM
beta = df / fm
print(f"modulaatioindeksi beta = {beta:.1f}")
# @loppu moduloi

# @alku besselit
# Sinimoduloidun FM:n spektriviivat ovat k*fm, amplitudit J_k(beta).
X = np.fft.fft(kanta) / len(kanta)
for k in range(9):
    mitattu = abs(X[round(k * fm)])           # bin k*fm, koska df = 1 Hz
    print(f"viiva {k} x fm: |J_k| = {abs(jv(k, beta)):.4f},"
          f" mitattu {mitattu:.4f}")
# @loppu besselit

# @alku kaista
teho = np.abs(np.fft.fftshift(X)) ** 2
f = np.fft.fftshift(np.fft.fftfreq(len(X), 1 / fs))
for B in (2 * df, 2 * (df + fm), 2 * (df + 2 * fm)):
    osuus = teho[np.abs(f) <= B / 2].sum() / teho.sum()
    print(f"kaista {B / 1e3:4.0f} kHz: tehosta {100 * osuus:.1f} %")
# @loppu kaista

# @alku demoduloi
# Hetkellinen taajuus = vaiheen muutos näytteiden välillä.
rng = np.random.default_rng(3)
kohina = 0.05 * (rng.standard_normal(len(kanta))
                 + 1j * rng.standard_normal(len(kanta)))
z = kanta * 0.3 + kohina                      # amplitudi ei vaikuta
taajuus = np.angle(z[1:] * np.conj(z[:-1])) * fs / (2 * np.pi)
sos = signal.butter(4, 3_000.0, fs=fs, output="sos")
palautettu = signal.sosfiltfilt(sos, taajuus) / df
virhe = np.std(palautettu[1_000:-1_000] - viesti[1:][1_000:-1_000])
print(f"demoduloitu, virheen keskihajonta {virhe:.4f}")
# @loppu demoduloi

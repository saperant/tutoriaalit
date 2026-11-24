"""Adaptiivinen hairionpoisto: verkkohurina viitesignaalin avulla."""

import numpy as np
from scipy import signal

# @alku tilanne
fs = 1_000.0
n = np.arange(20_000)
rng = np.random.default_rng(8)
# Hyotysignaali: kaistarajoitettua kohinaa (esim. biosignaali).
hyoty = signal.lfilter(*signal.butter(4, [5.0, 40.0], "bandpass", fs=fs),
                       rng.standard_normal(n.size))
# Verkkotaajuus vaeltaa hieman: kiintea lovi ei osu tarkasti.
f_verkko = 50.0 + 0.5 * np.sin(2 * np.pi * 0.05 * n / fs)
vaihe = 2 * np.pi * np.cumsum(f_verkko) / fs
viite = np.sin(vaihe) + 0.3 * np.sin(3 * vaihe)   # verkosta, puhdas
hurina = 0.8 * np.sin(vaihe + 1.1) + 0.2 * np.sin(3 * vaihe + 0.4)
d = hyoty + hurina                           # mitattu signaali
# @loppu tilanne

# @alku suodata
lkm, mu = 32, 0.01
w, v = np.zeros(lkm), np.zeros(lkm)
puhdistettu = np.zeros(n.size)
for i in range(n.size):
    v = np.roll(v, 1)
    v[0] = viite[i]
    puhdistettu[i] = d[i] - w @ v            # virhe = hyotysignaalin arvio
    w += mu / (1e-8 + v @ v) * puhdistettu[i] * v
# @loppu suodata


# @alku tulos
def snr(arvio: np.ndarray) -> float:
    loppu = slice(10_000, None)
    virhe = arvio[loppu] - hyoty[loppu]
    return float(10 * np.log10(np.sum(hyoty[loppu] ** 2)
                               / np.sum(virhe**2)))


lovi = signal.filtfilt(*signal.iirnotch(50.0, 30.0, fs=fs), d)
print(f"SNR mitattu            {snr(d):6.1f} dB")
print(f"SNR kiintea lovi 50 Hz {snr(lovi):6.1f} dB")
print(f"SNR adaptiivinen       {snr(puhdistettu):6.1f} dB")
# @loppu tulos

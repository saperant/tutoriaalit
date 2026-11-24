"""Lyhytaikainen Fourier-muunnos: liukuvan taajuuden seuranta."""

import numpy as np
from scipy import signal

# @alku stft
fs = 8_000.0
t = np.arange(int(2.0 * fs)) / fs
x = signal.chirp(t, f0=200, t1=2.0, f1=2_000)    # 200 -> 2000 Hz

ikkuna = signal.windows.hann(256, sym=False)
stft = signal.ShortTimeFFT(ikkuna, hop=128, fs=fs, scale_to="magnitude")
S = np.abs(stft.stft(x))            # rivit: taajuus, sarakkeet: aika
ajat = stft.t(len(x))
taajuudet = stft.f
print(f"kehyksiä {S.shape[1]}, taajuusväli {stft.delta_f:.2f} Hz,"
      f" aikaväli {1e3 * stft.delta_t:.1f} ms")
for hetki in (0.25, 0.75, 1.25, 1.75):
    j = int(np.argmin(np.abs(ajat - hetki)))
    arvio = taajuudet[np.argmax(S[:, j])]
    oikea = 200 + (2_000 - 200) * ajat[j] / 2.0
    print(f"t = {ajat[j]:.3f} s: huippu {arvio:6.1f} Hz,"
          f" oikea {oikea:6.1f} Hz")
# @loppu stft

# @alku kompromissi
# Napsahdus (impulssi) ja jatkuva 1000 Hz:n sävel: kuinka leveiltä ne
# näyttävät ajassa ja taajuudessa? Leveys = alue, jossa |S| > max/2.
napsahdus = np.zeros(int(0.5 * fs))
napsahdus[len(napsahdus) // 2] = 1.0
savel = np.sin(2 * np.pi * 1_000 * np.arange(int(0.5 * fs)) / fs)
for pituus in (64, 256, 1_024):
    w = signal.windows.hann(pituus, sym=False)
    s = signal.ShortTimeFFT(w, hop=8, fs=fs, mfft=8_192)
    Sn = np.abs(s.stft(napsahdus))
    aikaleveys = np.sum(Sn.max(axis=0) > Sn.max() / 2) * s.delta_t
    Ss = np.abs(s.stft(savel))
    keski = Ss[:, Ss.shape[1] // 2]
    kaistanleveys = np.sum(keski > keski.max() / 2) * s.delta_f
    print(f"ikkuna {pituus:4d}: napsahdus {1e3 * aikaleveys:6.1f} ms,"
          f" sävel {kaistanleveys:6.1f} Hz")
# @loppu kompromissi

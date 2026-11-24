"""Taajuusnaytteistys: mielivaltainen amplitudivaste firwin2:lla."""

import numpy as np
from scipy import signal

# @alku korjain
# Taajuuskorjain: korostaa 1-3 kHz kaistaa +6 dB (kerroin 2).
fs = 16_000.0
pisteet = [0.0, 800.0, 1_000.0, 3_000.0, 3_500.0, 8_000.0]
vahvistus = [1.0, 1.0, 2.0, 2.0, 1.0, 1.0]
h = signal.firwin2(127, pisteet, vahvistus, fs=fs)
f, H = signal.freqz(h, worN=[500.0, 2_000.0, 6_000.0], fs=fs)
for fi, Hi in zip(f, H, strict=True):
    db = round(20 * np.log10(abs(Hi)), 2) + 0.0     # ei miinusnollaa
    print(f"{fi:6.0f} Hz: {db:5.2f} dB")
# @loppu korjain

# @alku suora
# Sama ilman ikkunaa: taajuusnaytteet -> kaanteinen DFT. Pisteissa
# vaste on tasan haluttu, mutta pisteiden valissa se aaltoilee.
N = 63                                    # pariton: ei Nyquistin nayte
k = np.arange(N // 2 + 1)
haluttu = np.interp(k * fs / N, pisteet, vahvistus)
vaihe = np.exp(-1j * np.pi * k * (N - 1) / N)     # viive (N-1)/2
suora = np.fft.irfft(haluttu * vaihe, N)
fk, Hk = signal.freqz(suora, worN=k * fs / N, fs=fs)
fv, Hv = signal.freqz(suora, worN=(k[:-1] + 0.5) * fs / N, fs=fs)
virhe_k = np.max(np.abs(np.abs(Hk) - haluttu))
virhe_v = np.max(np.abs(np.abs(Hv) - np.interp(fv, pisteet, vahvistus)))
print(f"virhe pisteissa alle 1e-12: {virhe_k < 1e-12}")
print(f"virhe pisteiden valissa {virhe_v:.3f}")
# @loppu suora

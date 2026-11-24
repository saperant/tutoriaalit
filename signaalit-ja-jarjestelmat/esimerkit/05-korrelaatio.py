"""Viiveen arviointi ristikorrelaatiolla: kaiku kohinan seassa."""

import numpy as np
from scipy import signal

# @alku korrelaatio
rng = np.random.default_rng(5)
fs = 8_000.0
pulssi = signal.chirp(np.arange(400) / fs, f0=500, t1=400 / fs, f1=2_500)
viive_oikea = 1_234                       # näytettä
vastaanotettu = np.zeros(4_000)
vastaanotettu[viive_oikea:viive_oikea + len(pulssi)] += 0.3 * pulssi
vastaanotettu += 0.5 * rng.normal(size=len(vastaanotettu))

r = signal.correlate(vastaanotettu, pulssi, mode="full")
viiveet = signal.correlation_lags(len(vastaanotettu), len(pulssi))
arvio = int(viiveet[np.argmax(r)])
snr_naytteessa = 10 * np.log10(0.3**2 / 2 / 0.5**2)
print(f"SNR näytteittäin {snr_naytteessa:.1f} dB")
print(f"oikea viive {viive_oikea}, arvio {arvio} näytettä"
      f" = {1e3 * arvio / fs:.2f} ms")
# Korrelaatio on konvoluutio käännetyn pulssin kanssa.
print("correlate == convolve(x, pulssi[::-1]):",
      bool(np.allclose(r, np.convolve(vastaanotettu, pulssi[::-1]))))
# @loppu korrelaatio

"""Vaihe ja ryhmäviive: symmetrinen FIR vs. IIR."""

import numpy as np
from scipy import signal

# @alku vaihe
fir = signal.firwin(21, 0.25)                  # symmetrinen, 21 kerrointa
print("FIR symmetrinen:", bool(np.allclose(fir, fir[::-1])))
iir_b, iir_a = signal.butter(4, 0.25)

w = np.array([0.05, 0.2, 0.4, 0.6]) * np.pi
for nimi, b, a in (("FIR", fir, [1.0]), ("IIR", iir_b, iir_a)):
    _, gd = signal.group_delay((b, a), w=w)
    print(f"{nimi} ryhmäviive:", " ".join(f"{v:6.2f}" for v in gd),
          "näytettä")
# @loppu vaihe

# @alku pulssi
# Kapeakaistainen pulssi viivästyy ryhmäviiveen verran.
n = np.arange(600)
w0 = 0.2 * np.pi
verho = np.exp(-0.5 * ((n - 200) / 30.0) ** 2)
x = verho * np.cos(w0 * n)
for nimi, b, a in (("FIR", fir, [1.0]), ("IIR", iir_b, iir_a)):
    y = signal.lfilter(b, a, x)
    huippu = np.argmax(np.abs(signal.hilbert(y)))
    _, gd = signal.group_delay((b, a), w=[w0])
    print(f"{nimi}: verhokäyrän huippu siirtyi {int(huippu) - 200}"
          f" näytettä, ryhmäviive {gd[0]:.1f}")
# @loppu pulssi

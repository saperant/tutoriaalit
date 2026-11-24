"""Johdanto: mitkä taajuudet signaalissa on?"""

import numpy as np

# @alku taajuudet
fs = 1000                       # näytteitä sekunnissa
t = np.arange(fs) / fs          # yksi sekunti
x = 1.5 * np.sin(2 * np.pi * 50 * t) + 0.5 * np.cos(2 * np.pi * 120 * t)

X = np.fft.rfft(x)              # taajuustaso: kompleksiluvut
f = np.fft.rfftfreq(len(x), d=1 / fs)
amplitudi = 2 * np.abs(X) / len(x)

for k in np.argsort(amplitudi)[::-1][:2]:
    print(f"{f[k]:6.1f} Hz  amplitudi {amplitudi[k]:.3f}")
print(f"muiden taajuuksien suurin amplitudi < 1e-9: "
      f"{np.sort(amplitudi)[-3] < 1e-9}")
# @loppu taajuudet

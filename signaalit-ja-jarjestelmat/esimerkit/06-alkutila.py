"""Suotimen alkutila: nollatila vs. tasapainotila lfilter_zi:llä."""

import numpy as np
from scipy import signal

# @alku alkutila
b, a = signal.butter(2, 0.05)            # 2. asteen alipäästö
x = 5.0 + 0.1 * np.sin(0.02 * np.pi * np.arange(300))   # iso tasataso

nollasta = signal.lfilter(b, a, x)
zi = signal.lfilter_zi(b, a) * x[0]      # tila, jossa y = x[0] pysyvästi
tasapainosta, _ = signal.lfilter(b, a, x, zi=zi)

for n in (0, 10, 40, 100, 299):
    print(f"n = {n:3d}: x {x[n]:6.3f}   nollatila {nollasta[n]:6.3f}"
          f"   tasapaino {tasapainosta[n]:6.3f}")
# @loppu alkutila

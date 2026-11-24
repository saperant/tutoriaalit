"""Diskreetin konvoluution määritelmä."""

import numpy as np
from numpy.typing import NDArray

Taulukko = NDArray[np.float64]


# @alku oma
def konvoluutio(x: Taulukko, h: Taulukko) -> Taulukko:
    """y[n] = sum_k x[k] h[n - k], pituus len(x) + len(h) - 1."""
    y = np.zeros(len(x) + len(h) - 1)
    for n in range(len(y)):
        for k in range(len(x)):
            if 0 <= n - k < len(h):
                y[n] += x[k] * h[n - k]
    return y


x = np.array([1.0, 2.0, 3.0, 0.0, -1.0])
h = np.array([0.5, 0.25, 0.25])
print("oma        :", konvoluutio(x, h))
print("np.convolve:", np.convolve(x, h))
print("vaihdannainen:", bool(np.allclose(konvoluutio(h, x),
                                         konvoluutio(x, h))))
impulssi = np.array([0.0, 0.0, 1.0])            # viivästetty impulssi
print("x * viivästetty impulssi:", konvoluutio(x, impulssi))
# @loppu oma

"""Differenssiyhtälö: oma toteutus vs. scipy.signal.lfilter."""

import numpy as np
import numpy.typing as npt
from scipy import signal

Jono = npt.NDArray[np.float64]


# @alku suora
def suodata(b: Jono, a: Jono, x: Jono) -> Jono:
    """a[0] y[n] = sum_k b[k] x[n-k] - sum_{k>=1} a[k] y[n-k]."""
    if a[0] == 0:
        raise ValueError("a[0] ei saa olla nolla")
    b, a = b / a[0], a / a[0]
    y = np.zeros(len(x))
    for n in range(len(x)):
        summa = 0.0
        for k in range(len(b)):
            if n - k >= 0:
                summa += b[k] * x[n - k]
        for k in range(1, len(a)):
            if n - k >= 0:
                summa -= a[k] * y[n - k]
        y[n] = summa
    return y
# @loppu suora


# @alku vertailu
rng = np.random.default_rng(2)
x = rng.normal(size=200)
b = np.array([0.2, 0.4, 0.2])
a = np.array([2.0, -1.0, 0.4])           # a[0] != 1: normitus tarvitaan
print("oma == lfilter:", bool(np.allclose(suodata(b, a, x),
                                          signal.lfilter(b, a, x))))

d = np.zeros(12)
d[0] = 1.0
h = np.round(signal.lfilter(b, a, d), 3) + 0.0
print("impulssivaste:", " ".join(f"{v:6.3f}" for v in h[:8]))
print("FIR (a = [1]) on konvoluutio:",
      bool(np.allclose(signal.lfilter(b, [1.0], x),
                       np.convolve(x, b)[:len(x)])))
# @loppu vertailu

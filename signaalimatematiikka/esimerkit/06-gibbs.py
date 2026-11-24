"""Gibbsin ilmiö: ylitys ei pienene termejä lisäämällä."""

import math

import numpy as np
from numpy.typing import NDArray

Taulukko = NDArray[np.float64]


def osasumma(t: Taulukko, termejä: int) -> Taulukko:
    k = np.arange(1, 2 * termejä, 2)[:, np.newaxis]
    return np.asarray(np.sum(4 / (np.pi * k) * np.sin(k * t), axis=0))


# @alku gibbs
print("termejä   huippu   paikka t   pi/(2n)   ylitys hypystä")
for n in [5, 20, 100, 500]:
    t = np.linspace(1e-9, 2 * np.pi / (2 * n), 4001)  # ensimmäinen huippu
    y = osasumma(t, n)
    i = int(np.argmax(y))
    ylitys = (y[i] - 1) / 2                         # hyppy -1 -> 1 on 2
    print(f"{n:7d} {y[i]:8.4f} {t[i]:10.5f} {math.pi / (2 * n):9.5f}"
          f" {100 * ylitys:10.2f} %")
# @loppu gibbs

# @alku raja
# Raja-arvo (2/pi) Si(pi), Si(x) = int_0^x sin(u)/u du keskipistesääntönä.
n = 100000
u = (np.arange(n) + 0.5) * math.pi / n
si_pi = float(np.sum(np.sin(u) / u) * math.pi / n)
huippu = 2 / math.pi * si_pi
print(f"Si(pi) = {si_pi:.6f}, huippu (2/pi) Si(pi) = {huippu:.6f}")
print(f"ylitys = {100 * (huippu - 1) / 2:.3f} % hypyn korkeudesta")
# @loppu raja

# @alku keskineliö
t = 2 * np.pi * (np.arange(8192) + 0.5) / 8192
kantti = np.where(t < np.pi, 1.0, -1.0)
print("termejä   max |virhe|   keskineliövirhe")
for n in [5, 20, 100]:
    e = kantti - osasumma(t, n)
    print(f"{n:7d} {np.max(np.abs(e)):13.3f} {np.mean(e**2):17.5f}")
# @loppu keskineliö

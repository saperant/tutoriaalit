"""Tuntematon järjestelmä: impulssivaste, ennuste ja taajuusvaste."""

import numpy as np
import numpy.typing as npt

Jono = npt.NDArray[np.float64]


# @alku laatikko
def laatikko(x: Jono) -> Jono:
    """Anturin tasoitin, jonka sisältöä 'emme tiedä'."""
    y = np.zeros(len(x))
    edellinen = 0.0
    for n, arvo in enumerate(x):
        edellinen = 0.8 * edellinen + 0.2 * arvo
        y[n] = edellinen
    return y
# @loppu laatikko


# @alku impulssivaste
N = 40
impulssi = np.zeros(N)
impulssi[0] = 1.0
h = laatikko(impulssi)
print("h[0..5] =", " ".join(f"{v:.4f}" for v in h[:6]))

rng = np.random.default_rng(1)
x = rng.normal(size=N)
ennuste = np.convolve(x, h)[:N]           # y = x * h
todellinen = laatikko(x)
print("ennuste osuu:", bool(np.allclose(ennuste, todellinen)))
# @loppu impulssivaste

# @alku taajuusvaste
fs = 100.0                                # näytettä sekunnissa
n = np.arange(2000)
for f in (1.0, 10.0, 40.0):
    sini = np.sin(2 * np.pi * f / fs * n)
    y = laatikko(sini)
    mitattu = np.max(np.abs(y[1000:]))    # alkutransientti ohi
    k = np.arange(N)
    H = np.sum(h * np.exp(-2j * np.pi * f / fs * k))
    print(f"{f:4.0f} Hz: mitattu vahvistus {mitattu:.3f},"
          f" laskettu |H| {abs(H):.3f}")
# @loppu taajuusvaste

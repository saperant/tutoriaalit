"""Nopea konvoluutio FFT:llä: tulos ja kertolaskujen määrä."""

import math

import numpy as np
from scipy import signal

# @alku tulos
rng = np.random.default_rng(9)
x = rng.normal(size=10_000)
h = signal.firwin(501, 0.1)
suora = np.convolve(x, h)
fft = signal.fftconvolve(x, h)
lohkoittain = signal.oaconvolve(x, h)        # overlap-add FFT:llä
print("fftconvolve == convolve:", bool(np.allclose(fft, suora)))
print("oaconvolve == convolve:", bool(np.allclose(lohkoittain, suora)))
# @loppu tulos


# @alku laskenta
def suora_kertolaskut(nx: int, nh: int) -> int:
    return nx * nh


def fft_kertolaskut(nx: int, nh: int) -> int:
    """Kolme FFT:tä (2 eteen, 1 taakse) ja pistetulo, L = 2^k."""
    L = 1 << math.ceil(math.log2(nx + nh - 1))
    fft_yksi = (L // 2) * int(math.log2(L)) * 4   # radix-2, reaalikerrat
    return 3 * fft_yksi + 4 * L


for nh in (8, 32, 128, 1_024):
    s, f = suora_kertolaskut(10_000, nh), fft_kertolaskut(10_000, nh)
    print(f"Nh = {nh:5d}: suora {s:10,d}  FFT {f:10,d}"
          f"  {'FFT' if f < s else 'suora'} voittaa")
# @loppu laskenta

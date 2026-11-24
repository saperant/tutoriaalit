"""Polyfaasisuodinpankki: M kanavaa yhdella suotimella ja FFT:lla."""

import numpy as np
from scipy import signal

M, FS = 8, 800e3                      # 8 kanavaa, 100 kHz:n valein
h = signal.firwin(8 * 16, FS / M / 2, fs=FS)    # prototyyppialipaasto


# @alku suora
def suora(x: np.ndarray, kanava: int) -> np.ndarray:
    """Kanava kerrallaan: sekoitus, suodatus ja desimointi M:lla."""
    n = np.arange(len(x))
    siirretty = x * np.exp(-2j * np.pi * kanava * n / M)
    tulos: np.ndarray = signal.lfilter(h, [1.0], siirretty)[::M]
    return tulos
# @loppu suora


# @alku polyfaasi
def pankki(x: np.ndarray) -> np.ndarray:
    """Kaikki kanavat kerralla: M osasuodinta pienella naytetaajuudella
    ja M-pisteinen IFFT. Rivi k on kanava k."""
    lohkot = len(x) // M
    v = np.empty((M, lohkot), dtype=complex)
    for r in range(M):
        # Osasuodin h[pM + r] ja osajono x[mM - r] (x[negatiivinen] = 0).
        x_r = np.concatenate([np.zeros(1), x[M - r::M]])[:lohkot] \
            if r else x[::M][:lohkot]
        v[r] = signal.lfilter(h[r::M], [1.0], x_r)
    tulos: np.ndarray = M * np.fft.ifft(v, axis=0)
    return tulos
# @loppu polyfaasi


# @alku ajo
rng = np.random.default_rng(12)
n = np.arange(M * 4096)
x = (np.exp(2j * np.pi * 103e3 * n / FS) + 0.1 * np.exp(2j * np.pi * 310e3
     * n / FS) + 0.01 * np.exp(2j * np.pi * -205e3 * n / FS))
x += 1e-4 * (rng.standard_normal(len(n)) + 1j * rng.standard_normal(len(n)))
y = pankki(x)
ero = max(np.max(np.abs(y[k] - suora(x, k))) for k in range(M))
print(f"polyfaasi vs. suora: {'sama' if ero < 1e-9 else 'ERI'} (ero < 1e-9)")
for k in range(M):
    keski = (k if k < M // 2 else k - M) * FS / M
    teho = 10 * np.log10(np.mean(np.abs(y[k, 100:]) ** 2))
    print(f"kanava {k} ({keski / 1e3:+5.0f} kHz): {teho:4.0f} dB")
# Suora tapa laskee vain joka M:nnen lahdon: len(h) / M kanavaa kohti.
print(f"kertolaskuja tulonaytetta kohti: suora {M * len(h) // M}, "
      f"polyfaasi {len(h) // M} + FFT {np.log2(M) / 2:.1f}")
# @loppu ajo

"""Butterworth, Chebyshev ja elliptinen: aste samalle vaatimukselle."""

import numpy as np
from scipy import signal

# @alku asteet
fs, paasto, esto = 8_000.0, 1_000.0, 1_500.0
Rp, As = 0.1, 60.0                         # aaltoilu ja vaimennus (dB)


def suunnittele(nimi: str) -> tuple[int, np.ndarray]:
    """Pienin aste, joka tayttaa vaatimuksen, ja suodin lohkoina."""
    if nimi == "butter":
        n, raja = signal.buttord(paasto, esto, Rp, As, fs=fs)
        return n, signal.butter(n, raja, output="sos", fs=fs)
    if nimi == "cheby1":
        n, raja = signal.cheb1ord(paasto, esto, Rp, As, fs=fs)
        return n, signal.cheby1(n, Rp, raja, output="sos", fs=fs)
    if nimi == "cheby2":
        n, raja = signal.cheb2ord(paasto, esto, Rp, As, fs=fs)
        return n, signal.cheby2(n, As, raja, output="sos", fs=fs)
    n, raja = signal.ellipord(paasto, esto, Rp, As, fs=fs)
    return n, signal.ellip(n, Rp, As, raja, output="sos", fs=fs)


print("tyyppi  aste  aaltoilu  vaimennus  viive 500 Hz  viive max")
for nimi in ("butter", "cheby1", "cheby2", "ellip"):
    aste, sos = suunnittele(nimi)
    f, H = signal.sosfreqz(sos, worN=1 << 15, fs=fs)
    db = 20 * np.log10(np.maximum(np.abs(H), 1e-15))
    aaltoilu = db[f <= paasto].max() - db[f <= paasto].min()
    vaimennus = -db[f >= esto].max()
    b, a = signal.sos2tf(sos)
    fv, gd = signal.group_delay((b, a), w=np.linspace(10, paasto, 200),
                                fs=fs)
    viive500 = float(np.interp(500.0, fv, gd))
    print(f"{nimi:7s} {aste:4d} {aaltoilu:7.3f} dB {vaimennus:6.1f} dB"
          f" {viive500:9.1f} {gd.max():12.1f}")
# @loppu asteet

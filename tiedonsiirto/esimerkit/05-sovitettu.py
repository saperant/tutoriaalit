"""Sovitettu suodin maksimoi SNR:n: vertailu muihin vastaanottosuotimiin."""

import numpy as np
from scipy import signal

sps, janne, beta = 16, 16, 0.35
t = np.arange(-janne * sps // 2, janne * sps // 2 + 1) / sps


def rrc() -> np.ndarray:
    """Juurikorotettu kosini, energia 1."""
    h = np.empty_like(t)
    for i, ti in enumerate(t):
        if np.isclose(ti, 0.0):
            h[i] = 1 + beta * (4 / np.pi - 1)
        elif np.isclose(abs(ti), 1 / (4 * beta)):
            h[i] = beta / np.sqrt(2) * (
                (1 + 2 / np.pi) * np.sin(np.pi / (4 * beta))
                + (1 - 2 / np.pi) * np.cos(np.pi / (4 * beta)))
        else:
            h[i] = (np.sin(np.pi * ti * (1 - beta))
                    + 4 * beta * ti * np.cos(np.pi * ti * (1 + beta))) / (
                np.pi * ti * (1 - (4 * beta * ti) ** 2))
    tulos: np.ndarray = h / np.sqrt(np.sum(h**2))
    return tulos


# @alku vertailu
# Lähetetty pulssi p on RRC. Vastaanottosuodin g. Näytteen signaali on
# huipun arvo (p * g)[0], kohinan teho N0 * sum(g^2). Paras mahdollinen
# SNR on Es/N0, ja sen antaa g = p käännettynä (sovitettu suodin).
p = rrc()
ehdokkaat = {
    "sovitettu (RRC)": p[::-1],
    "integroi T (laatikko)": np.ones(sps),
    "Butterworth 4, 0.5/T": signal.lfilter(
        *signal.butter(4, 0.5 / sps * 2), np.r_[1.0, np.zeros(20 * sps)]),
}
for nimi, g in ehdokkaat.items():
    y = np.convolve(p, g)
    huippu = int(np.argmax(np.abs(y)))
    snr = y[huippu] ** 2 / np.sum(g**2)       # suhteessa Es/N0:aan
    naytteet = y[huippu % sps::sps]
    isi = (np.sum(np.abs(naytteet)) - abs(y[huippu])) / abs(y[huippu])
    menetys = round(-10 * np.log10(snr), 2) + 0.0
    print(f"{nimi:22s} SNR-menetys {menetys:5.2f} dB,"
          f" ISI {isi:.3f}")
# @loppu vertailu

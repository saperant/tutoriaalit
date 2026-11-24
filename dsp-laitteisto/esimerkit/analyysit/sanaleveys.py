"""Sanaleveyksien vaikutus FIR-suotimen tarkkuuteen: ulostulon
pyöristys vai katkaisu, ja kertoimien bittimäärä.

Käyttö: python3 analyysit/sanaleveys.py
"""

from __future__ import annotations

import math
import random

import numpy as np
from scipy import signal

from malli.kertoimet import DATA_BITIT, FIR, KERROIN_MURTO
from malli.kiintea import kvantisoi
from malli.suotimet import fir


# @alku virhe
def virhe(pyoristys: bool) -> tuple[float, float]:
    """Ulostulon virhe tarkkaan (liukuluku)suodatukseen nähden: keskiarvo
    ja SNR. Sama kvantisoitu sisääntulo molemmille."""
    rng = random.Random(1)
    x = [rng.randint(-1024, 1023) for _ in range(20000)]
    y = np.array(fir(x, FIR, KERROIN_MURTO, DATA_BITIT, pyoristys=pyoristys))
    tarkka = np.convolve(x, np.array(FIR) / (1 << KERROIN_MURTO))[: len(x)]
    e = y - tarkka
    snr = 10 * math.log10(float(np.mean(tarkka**2) / np.mean(e**2)))
    return float(np.mean(e)), snr
    # @loppu virhe


# @alku kertoimet
def estokaista(bitit: int | None) -> float:
    """Suurin vahvistus estokaistalla (f >= 0.35 fs), kun kertoimet
    kvantisoidaan bitit-levyisiksi (Q1.(bitit-1)); None = liukuluvut."""
    h = signal.firwin(32, 0.5)
    q = [
        float(v)
        if bitit is None
        else kvantisoi(float(v), bitit - 1, bitit) / (1 << (bitit - 1))
        for v in h
    ]
    w, vaste = signal.freqz(q, worN=4096)
    esto = np.abs(vaste[w >= 0.7 * math.pi])
    return 20 * math.log10(float(esto.max()))
    # @loppu kertoimet


def main() -> None:
    print("ulostulo   keskivirhe   SNR")
    for nimi, pyoristys in (("pyöristys", True), ("katkaisu", False)):
        ka, snr = virhe(pyoristys)
        print(f"{nimi:9}  {ka:+.3f} LSB  {snr:5.1f} dB")
    print()
    print("32 kerrointa, kerroinbitit -> suurin vahvistus estokaistalla")
    for bitit in (8, 10, 12, 14, 16):
        print(f"{bitit:2} bittiä:   {estokaista(bitit):6.1f} dB")
    print(f"liukuluku:   {estokaista(None):6.1f} dB")


if __name__ == "__main__":
    main()

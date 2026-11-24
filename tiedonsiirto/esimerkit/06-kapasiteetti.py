"""Kuinka kaukana modulaatiot ovat Shannonin rajasta?"""

import numpy as np
from scipy.optimize import brentq
from scipy.special import erfc


def Q(x: float) -> float:
    return float(0.5 * erfc(x / np.sqrt(2)))


def ber(M: int, EbN0: float) -> float:
    """Gray-koodatun PSK:n (M <= 8) tai neliö-QAM:n likimääräinen BER."""
    k = np.log2(M)
    if M <= 4:
        return Q(np.sqrt(2 * EbN0))
    if M == 8:
        return float(2 / k * Q(np.sqrt(2 * k * EbN0) * np.sin(np.pi / M)))
    return float(4 / k * (1 - 1 / np.sqrt(M))
                 * Q(np.sqrt(3 * k * EbN0 / (M - 1))))


# @alku raja
# Shannon: C/B = log2(1 + SNR). Kun bittejä siirretään eta bit/s/Hz,
# SNR = eta Eb/N0, joten Eb/N0 >= (2^eta - 1) / eta.
def shannon_EbN0_dB(eta: float) -> float:
    return float(10 * np.log10((2**eta - 1) / eta))


print(f"raja, kun eta -> 0: {10 * np.log10(np.log(2)):.2f} dB")
print("modulaatio  bit/s/Hz  Eb/N0 @ 1e-6  Shannon   väli")
for nimi, M in (("BPSK", 2), ("QPSK", 4), ("8-PSK", 8),
                ("16-QAM", 16), ("64-QAM", 64), ("256-QAM", 256)):
    # Nyquist-pulssi beta = 0: symbolinopeus = kaistanleveys.
    eta = float(np.log2(M))
    tarve = brentq(lambda x, M=M: ber(M, 10 ** (x / 10)) - 1e-6, -5, 40)
    raja = shannon_EbN0_dB(eta)
    print(f"{nimi:10s} {eta:7.0f}  {tarve:9.1f} dB  {raja:5.1f} dB"
          f"  {tarve - raja:4.1f} dB")
# @loppu raja

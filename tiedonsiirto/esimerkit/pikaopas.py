"""Pikaoppaan apufunktiot: desibelit, Q-funktio, BER ja kohina."""

import numpy as np
from scipy.special import erfc

rng = np.random.default_rng(0)


# @alku muunnokset
def Q(x: float) -> float:
    """P(N(0, 1) > x)."""
    return float(0.5 * erfc(x / np.sqrt(2)))


def EsN0_dB(EbN0_dB: float, M: int) -> float:
    """Symbolin energia: log2(M) bittiä symbolia kohti."""
    return float(EbN0_dB + 10 * np.log10(np.log2(M)))


def snr_naytteella_dB(EsN0_dB: float, sps: int) -> float:
    """SNR näytettä kohti, kun signaalissa on sps näytettä/symboli."""
    return float(EsN0_dB - 10 * np.log10(sps))
# @loppu muunnokset


# @alku kohina
def awgn(x: np.ndarray, EsN0_dB: float) -> np.ndarray:
    """Kompleksinen AWGN symboleille, joiden keskienergia on 1.

    Näytteistetylle signaalille sama toimii, kun pulssin energia on 1 ja
    kohina lisätään ennen sovitettua suodinta (ks. luku 6).
    """
    N0 = 10 ** (-EsN0_dB / 10)
    sigma = np.sqrt(N0 / 2)                   # kumpaankin komponenttiin
    kohina = sigma * (rng.standard_normal(x.shape)
                      + 1j * rng.standard_normal(x.shape))
    y: np.ndarray = x + kohina
    return y
# @loppu kohina


# @alku ber
def ber_bpsk(EbN0_dB: float) -> float:
    return Q(np.sqrt(2 * 10 ** (EbN0_dB / 10)))


def ber_qam(M: int, EbN0_dB: float) -> float:
    """Gray-koodattu neliö-QAM, lähimpien naapurien likiarvo."""
    k, g = np.log2(M), 10 ** (EbN0_dB / 10)
    return float(4 / k * (1 - 1 / np.sqrt(M))
                 * Q(np.sqrt(3 * k * g / (M - 1))))


print(f"Es/N0 = {EsN0_dB(10, 16):.2f} dB (16-QAM, Eb/N0 10 dB)")
print(f"SNR/näyte = {snr_naytteella_dB(16.02, 8):.2f} dB (sps 8)")
print(f"BPSK 9.6 dB: {ber_bpsk(9.6):.1e}, 16-QAM 13.4 dB:"
      f" {ber_qam(16, 13.4):.1e}")
y = awgn(np.ones(100_000, dtype=complex), 10.0)
print(f"mitattu Es/N0 {-10 * np.log10(np.mean(np.abs(y - 1) ** 2)):.1f} dB")
# @loppu ber

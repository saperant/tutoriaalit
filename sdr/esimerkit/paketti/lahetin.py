"""2-GFSK-pakettilahetin: alkuosa, tahdistussana, pituus, data ja CRC.

Kehys on tyypillinen ISM-kaistan anturiradioille (esim. TI:n CC1101-
ja Semtechin SX127x-piirien FSK-tila): 0xAA-alkuosa vastaanottimen
taajuuden ja ajoituksen hakuun, 16 bitin tahdistussana, pituustavu,
data ja CRC-16.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy import signal

Reaali = NDArray[np.float64]
Kompleksi = NDArray[np.complex128]

# @alku parametrit
FS = 912_000.0             # tallenteen naytetaajuus
BITTINOPEUS = 38_000.0     # 24 naytetta bittia kohti
POIKKEAMA = 19_000.0       # +-19 kHz: modulaatioindeksi h = 1
BT = 0.5                   # Gaussin suotimen kaistanleveys x bittiaika
ALKUOSA = bytes([0xAA] * 4)
TAHDISTUS = bytes([0xD3, 0x91])
# @loppu parametrit


# @alku crc
def crc16(data: bytes) -> int:
    """CRC-16/CCITT-FALSE: polynomi 0x1021, alkuarvo 0xFFFF."""
    crc = 0xFFFF
    for tavu in data:
        crc ^= tavu << 8
        for _ in range(8):
            crc = (crc << 1 ^ 0x1021 if crc & 0x8000 else crc << 1) & 0xFFFF
    return crc


def kehys(data: bytes) -> bytes:
    """Alkuosa, tahdistus, pituus, data ja CRC (pituudesta dataan)."""
    if len(data) > 255:
        raise ValueError("data on enintaan 255 tavua")
    runko = bytes([len(data)]) + data
    return ALKUOSA + TAHDISTUS + runko + crc16(runko).to_bytes(2, "big")


def bitit(tavut: bytes) -> list[int]:
    return [t >> i & 1 for t in tavut for i in range(7, -1, -1)]
# @loppu crc


# @alku gfsk
def gaussin_pulssi(sps: int) -> Reaali:
    """Gaussin suodin, jonka pinta-ala on 1 bittiajan verran (4 bittia)."""
    t = np.arange(-2 * sps, 2 * sps + 1) / sps
    sigma = np.sqrt(np.log(2)) / (2 * np.pi * BT)
    h = np.exp(-t**2 / (2 * sigma**2))
    tulos: Reaali = h / h.sum()
    return tulos


def gfsk(b: list[int], fs: float = FS) -> Kompleksi:
    """Bitit taajuudeksi (+-POIKKEAMA), Gaussin suodatus ja vaihe."""
    sps = round(fs / BITTINOPEUS)
    nrz = np.repeat(2.0 * np.array(b) - 1.0, sps)
    taajuus = POIKKEAMA * signal.convolve(nrz, gaussin_pulssi(sps), "same")
    z: Kompleksi = np.exp(2j * np.pi * np.cumsum(taajuus) / fs)
    return z
# @loppu gfsk


# @alku tallenne
def tallenne(paketit: list[tuple[float, bytes, float, float]],
             kesto: float, keskitaajuus: float,
             rng: np.random.Generator) -> Kompleksi:
    """Kaista, jossa paketit (aika s, data, Eb/N0 dB, taajuusvirhe Hz).

    Kohinan taso on 1 koko kaistalla; paketin teho asetetaan niin, etta
    Eb/N0 toteutuu: Eb = P / R ja N0 = 1 / FS."""
    n = round(kesto * FS)
    x: Kompleksi = (rng.standard_normal(n)
                    + 1j * rng.standard_normal(n)) / np.sqrt(2)
    for aika, data, ebn0_db, virhe in paketit:
        z = gfsk(bitit(kehys(data)))
        teho = 10 ** (ebn0_db / 10) * BITTINOPEUS / FS
        alku = round(aika * FS)
        k = np.arange(alku, alku + len(z))
        siirto = np.exp(2j * np.pi * (keskitaajuus + virhe) * k / FS)
        x[k] += np.sqrt(teho) * z * siirto * np.exp(1j * rng.uniform(0, 6))
    return x
# @loppu tallenne

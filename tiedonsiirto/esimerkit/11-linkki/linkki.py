"""Pieni kokonainen pakettilinkki: QPSK, RRC, tahdistus ja CRC.

Lähetin: tavut -> bitit + CRC-16 -> QPSK -> alkuosa eteen -> RRC.
Kanava: viive, taajuus- ja vaihevirhe, AWGN.
Vastaanotin: sovitettu suodin -> kehyksen ja ajoituksen haku alkuosan
korrelaatiolla -> taajuus- ja vaihe-estimaatti alkuosasta -> päätökset
-> CRC-tarkistus.
"""

import binascii
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

Kompleksi = npt.NDArray[np.complex128]
Reaali = npt.NDArray[np.float64]

SPS, BETA, JANNE = 4, 0.35, 8
BARKER = np.array([1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1], dtype=float)
# Alkuosa: Barker kahdesti peräkkäin (taajuusestimaattia varten), QPSK:n
# kulmapisteinä. 26 symbolia.
ALKUOSA: Kompleksi = np.tile(BARKER, 2) * (1 + 1j) / np.sqrt(2)


def rrc() -> Reaali:
    """Juurikorotettu kosini, energia 1."""
    t = np.arange(-JANNE * SPS // 2, JANNE * SPS // 2 + 1) / SPS
    h = np.empty_like(t)
    for i, ti in enumerate(t):
        if np.isclose(ti, 0.0):
            h[i] = 1 + BETA * (4 / np.pi - 1)
        elif np.isclose(abs(ti), 1 / (4 * BETA)):
            h[i] = BETA / np.sqrt(2) * (
                (1 + 2 / np.pi) * np.sin(np.pi / (4 * BETA))
                + (1 - 2 / np.pi) * np.cos(np.pi / (4 * BETA)))
        else:
            h[i] = (np.sin(np.pi * ti * (1 - BETA))
                    + 4 * BETA * ti * np.cos(np.pi * ti * (1 + BETA))) / (
                np.pi * ti * (1 - (4 * BETA * ti) ** 2))
    tulos: Reaali = h / np.sqrt(np.sum(h**2))
    return tulos


H = rrc()


# @alku lahetin
def bitit(data: bytes) -> npt.NDArray[np.uint8]:
    """Tavut ja niiden CRC-16 (CCITT) biteiksi."""
    crc = binascii.crc_hqx(data, 0xFFFF)
    return np.unpackbits(np.frombuffer(data + crc.to_bytes(2, "big"),
                                       dtype=np.uint8))


def laheta(data: bytes) -> Kompleksi:
    b = bitit(data).astype(np.float64)
    symbolit = ((1 - 2 * b[0::2]) + 1j * (1 - 2 * b[1::2])) / np.sqrt(2)
    kaikki = np.concatenate([ALKUOSA, symbolit])
    nostettu = np.zeros(len(kaikki) * SPS, dtype=complex)
    nostettu[::SPS] = kaikki
    tulos: Kompleksi = np.convolve(nostettu, H).astype(np.complex128)
    return tulos
# @loppu lahetin


# @alku kanava
@dataclass
class Kanava:
    viive: int = 0                            # näytteinä
    taajuus: float = 0.0                      # sykliä näytettä kohti
    vaihe: float = 0.0                        # radiaaneina
    EbN0_dB: float = 100.0

    def lapi(self, x: Kompleksi, rng: np.random.Generator) -> Kompleksi:
        y = np.concatenate([np.zeros(self.viive, dtype=complex), x,
                            np.zeros(64, dtype=complex)])
        n = np.arange(len(y))
        y = y * np.exp(1j * (2 * np.pi * self.taajuus * n + self.vaihe))
        # Pulssin energia 1 per symboli, Es = 1, Eb = Es / 2.
        N0 = 1 / (2 * 10 ** (self.EbN0_dB / 10))
        kohina = np.sqrt(N0 / 2) * (rng.standard_normal(len(y))
                                    + 1j * rng.standard_normal(len(y)))
        tulos: Kompleksi = y + kohina
        return tulos
# @loppu kanava


# @alku vastaanotin
def seuraa(s: Kompleksi, Kp: float = 0.05, Ki: float = 0.002) -> Kompleksi:
    """Päätösohjattu vaiheen seuranta: alkuosan estimaatin jäännösvirhe
    kasvaisi pitkässä paketissa, joten vaihetta korjataan symboleittain."""
    y = np.empty_like(s)
    vaihe = taajuus = 0.0
    for i, si in enumerate(s):
        y[i] = si * np.exp(-1j * vaihe)
        paatos = (np.sign(y[i].real) + 1j * np.sign(y[i].imag)) / np.sqrt(2)
        e = float(np.angle(y[i] * np.conj(paatos)))
        taajuus += Ki * e
        vaihe += Kp * e + taajuus
    return y


def vastaanota(r: Kompleksi, tavuja: int,
               seuranta: bool = True) -> bytes | None:
    """Etsii paketin ja palauttaa datan, tai None, jos CRC ei täsmää."""
    z = np.convolve(r, H)
    # Kehys ja ajoitus: alkuosan korrelaatio kaikilla näytevaiheilla.
    viite = np.zeros(len(ALKUOSA) * SPS, dtype=complex)
    viite[::SPS] = ALKUOSA
    c = np.abs(np.correlate(z, viite, "valid"))
    alku = int(np.argmax(c))
    naytteet = z[alku::SPS]
    symboleja = len(ALKUOSA) + 4 * (tavuja + 2)
    if len(naytteet) < symboleja:
        return None
    s = naytteet[:symboleja]
    # Taajuus: alkuosan puoliskojen vaihe-ero (13 symbolin välein).
    eka = s[:13] * np.conj(ALKUOSA[:13])
    toka = s[13:26] * np.conj(ALKUOSA[13:26])
    w = np.angle(np.sum(toka * np.conj(eka))) / 13     # rad/symboli
    s = s * np.exp(-1j * w * np.arange(symboleja))
    # Vaihe: korrelaatio alkuosaan taajuuskorjauksen jälkeen.
    s = s * np.exp(-1j * np.angle(np.vdot(ALKUOSA, s[: len(ALKUOSA)])))
    data = s[len(ALKUOSA):]
    if seuranta:
        data = seuraa(data)
    b = np.empty(2 * len(data), dtype=np.uint8)
    b[0::2] = data.real < 0
    b[1::2] = data.imag < 0
    tavut = np.packbits(b).tobytes()
    viesti, crc = tavut[:tavuja], tavut[tavuja:]
    if binascii.crc_hqx(viesti, 0xFFFF).to_bytes(2, "big") != crc:
        return None
    return viesti
# @loppu vastaanotin

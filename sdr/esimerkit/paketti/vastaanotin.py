"""2-GFSK-pakettivastaanotin: kanava, ilmaisu, haku, ajoitus ja CRC."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy import signal

import lahetin as lh

Reaali = NDArray[np.float64]
Kompleksi = NDArray[np.complex128]

DESIMOINTI = 6                         # 912 kHz -> 152 kHz, 4 nayt./bitti
SPS = round(lh.FS / DESIMOINTI / lh.BITTINOPEUS)


@dataclass
class Paketti:
    alku_ms: float
    taajuusvirhe_hz: float
    data: bytes
    crc_ok: bool


# @alku kanava
def kanava(x: Kompleksi, keskitaajuus: float) -> Kompleksi:
    """Siirto, 50 kHz:n alipaasto (Carson 2 x (19 + 19) kHz), desimointi."""
    n = np.arange(len(x))
    h = signal.firwin(97, 50e3, fs=lh.FS)
    siirretty = x * np.exp(-2j * np.pi * keskitaajuus * n / lh.FS)
    y: Kompleksi = signal.upfirdn(h, siirretty, down=DESIMOINTI)
    return y[len(h) // (2 * DESIMOINTI):]
# @loppu kanava


# @alku ilmaisu
def taajuus(z: Kompleksi) -> Reaali:
    """Hetkellinen taajuus poikkeaman yksikoissa: bitti 1 = +1, 0 = -1."""
    fs = lh.FS / DESIMOINTI
    f: Reaali = np.angle(z[1:] * np.conj(z[:-1])) * fs / (
        2 * np.pi * lh.POIKKEAMA)
    return f


def mallipohja() -> Reaali:
    """Alkuosan ja tahdistussanan odotettu taajuuskayra."""
    b = lh.bitit(lh.ALKUOSA + lh.TAHDISTUS)
    pohja: Reaali = np.repeat(2.0 * np.array(b) - 1.0, SPS)
    return pohja


def hae(f: Reaali, kynnys: float = 0.45) -> list[int]:
    """Normitettu ristikorrelaatio: kohdat, joissa malli alkaa."""
    pohja = mallipohja() - mallipohja().mean()
    c = signal.correlate(f, pohja, "valid")
    energia = signal.correlate(f**2, np.ones(len(pohja)), "valid")
    rho = c / np.sqrt(np.maximum(energia, 1e-12) * (pohja**2).sum())
    loydot: list[int] = []
    for k in np.flatnonzero(rho > kynnys):
        if loydot and k - loydot[-1] < len(pohja):
            if rho[k] > rho[loydot[-1]]:
                loydot[-1] = int(k)          # sama paketti: huippu talteen
            continue
        loydot.append(int(k))
    return loydot
# @loppu ilmaisu


# @alku pura
def pura(f: Reaali, alku: int) -> Paketti:
    """Taajuusvirhe alkuosasta, integroi ja paata -suodatin ja CRC."""
    alkuosa = f[alku:alku + 8 * len(lh.ALKUOSA) * SPS]
    virhe = float(alkuosa.mean())             # 1010...-kuvion keskiarvo 0
    data_alku = alku + 8 * (len(lh.ALKUOSA) + len(lh.TAHDISTUS)) * SPS

    def tavut(maara: int, kohta: int) -> bytes:
        osa = f[kohta:kohta + 8 * maara * SPS] - virhe
        if len(osa) < 8 * maara * SPS:
            return bytes(maara)               # tallenne loppui kesken
        summat = osa.reshape(-1, SPS).sum(axis=1)
        b = (summat > 0).astype(int)
        return bytes(int("".join(map(str, b[i:i + 8])), 2)
                     for i in range(0, len(b), 8))

    pituus = tavut(1, data_alku)[0]
    runko = tavut(1 + pituus + 2, data_alku)
    ok = lh.crc16(runko[:-2]) == int.from_bytes(runko[-2:], "big")
    fs = lh.FS / DESIMOINTI
    return Paketti(1e3 * alku / fs, virhe * lh.POIKKEAMA,
                   runko[1:-2], ok)
# @loppu pura


# @alku vastaanota
def vastaanota(x: Kompleksi, keskitaajuus: float) -> list[Paketti]:
    """Koko ketju: kanava, ilmaisu, haku ja purku jokaiselle loydolle."""
    f = taajuus(kanava(x, keskitaajuus))
    return [pura(f, alku) for alku in hae(f)]
# @loppu vastaanota

"""Synteettinen FM-yleisradiotallenne: stereoasema, pilotti ja RDS.

Tallenne korvaa oikean radion: se on tehty samoilla parametreilla kuin
FM-yleisradiolahetys (75 kHz:n poikkeama, 19 kHz:n pilotti, 38 kHz:n
erotuskanava ja 57 kHz:n datakanava), ja siihen lisataan kohina,
viereinen asema ja RTL-SDR:n 8-bittinen kvantisointi.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from scipy import signal

import rds

Reaali = NDArray[np.float64]
Kompleksi = NDArray[np.complex128]

# @alku parametrit
FS_IQ = 912_000.0          # tallenteen naytetaajuus (RTL-SDR: 0,9-3,2 MS/s)
FS_MPX = 228_000.0         # MPX-signaalin naytetaajuus, 12 x 19 kHz
PILOTTI = 19_000.0         # pilotti; erotuskanava 2x, RDS 3x
POIKKEAMA = 75_000.0       # FM-yleisradion huippupoikkeama
TAU = 50e-6                # esikorostuksen aikavakio Euroopassa
RDS_BITTINOPEUS = 57_000.0 / 48   # 1187,5 bit/s
VASEN_HZ, OIKEA_HZ = 700.0, 1_900.0   # testiaanet kanavilla
# @loppu parametrit


# @alku esikorostus
def esikorostus(x: Reaali, fs: float) -> Reaali:
    """50 us:n esikorostus (1 + s tau), napa 20 kHz:ssa rajaamaan."""
    tau2 = 1 / (2 * np.pi * 20e3)
    b, a = signal.bilinear([TAU, 1.0], [tau2, 1.0], fs)
    y: Reaali = signal.lfilter(b, a, x)
    return y
# @loppu esikorostus


# @alku rdskanta
def rds_kanta(bitit: list[int], n: int, fs: float) -> Reaali:
    """Differentiaalikoodaus ja kaksivaihekoodaus (biphase) kantataajuudelle.

    Jokainen bitti on puoliksi +1 ja puoliksi -1 kerrottuna merkilla;
    alipaastosuodin rajaa kaistan noin 2,4 kHz:iin."""
    d = np.bitwise_xor.accumulate(np.array(bitit, dtype=np.int64))
    merkit = 2.0 * d - 1.0
    puoli = round(fs / RDS_BITTINOPEUS / 2)
    pulssi = np.concatenate([np.ones(puoli), -np.ones(puoli)])
    aalto = np.kron(merkit, pulssi)
    aalto = np.resize(aalto, n)               # toistetaan tarvittaessa
    h = signal.firwin(255, 2_400.0, fs=fs)
    y: Reaali = signal.lfilter(h, [1.0], aalto)
    return y
# @loppu rdskanta


# @alku mpx
def mpx(kesto: float, nimi: str, pi: int, rng: np.random.Generator,
        pilotin_virhe_hz: float = 1.5) -> Reaali:
    """Stereo-MPX: summa, pilotti, erotus 38 kHz:lla ja RDS 57 kHz:lla."""
    n = round(kesto * FS_MPX)
    t = np.arange(n) / FS_MPX
    vasen = esikorostus(0.5 * np.sin(2 * np.pi * VASEN_HZ * t), FS_MPX)
    oikea = esikorostus(0.4 * np.sin(2 * np.pi * OIKEA_HZ * t), FS_MPX)
    phi = 2 * np.pi * (PILOTTI + pilotin_virhe_hz) * t + rng.uniform(0, 6)
    ryhmat = [rds.ryhma_0a(pi, 10, nimi, osa % 4) for osa in range(40)]
    bitit = rds.bitit(s for r in ryhmat for s in r)
    data = rds_kanta(bitit, n, FS_MPX)
    tulos: Reaali = (0.9 * ((vasen + oikea) / 2
                            + (vasen - oikea) / 2 * np.cos(2 * phi))
                     + 0.09 * np.cos(phi) + 0.05 * data * np.cos(3 * phi))
    return tulos
# @loppu mpx


# @alku moduloi
def fm(m: Reaali, fs_mpx: float, fs: float) -> Kompleksi:
    """Ylinaytteistys tallenteen taajuudelle ja FM-modulointi."""
    ylos = round(fs / fs_mpx)
    m_iq = signal.resample_poly(m, ylos, 1)
    vaihe = 2 * np.pi * POIKKEAMA * np.cumsum(m_iq) / fs
    z: Kompleksi = np.exp(1j * vaihe)
    return z


def tallenne(kesto: float, cnr_db: float, rng: np.random.Generator,
             asema_hz: float = 200e3) -> Kompleksi:
    """Kaista, jossa asema, heikompi naapuriasema ja kohina."""
    n = np.arange(round(kesto * FS_IQ))
    asema = fm(mpx(kesto, "TESTI FM", 0x6A01, rng), FS_MPX, FS_IQ)
    t_mpx = np.arange(len(n) // 4) / FS_MPX
    naapuri = fm(0.3 * np.sin(2 * np.pi * 400 * t_mpx), FS_MPX, FS_IQ)
    x = (asema * np.exp(2j * np.pi * asema_hz * n / FS_IQ)
         + 0.3 * naapuri * np.exp(-2j * np.pi * 250e3 * n / FS_IQ))
    # CNR mitataan 200 kHz:n kanavakaistalla, kohina on koko kaistalla.
    n0 = 10 ** (-cnr_db / 10) * FS_IQ / 200e3
    kohina = np.sqrt(n0 / 2) * (rng.standard_normal(len(n))
                                + 1j * rng.standard_normal(len(n)))
    tulos: Kompleksi = x + kohina
    return tulos
# @loppu moduloi


# @alku cu8
def kirjoita_cu8(polku: Path, x: Kompleksi, taysi: float) -> None:
    """RTL-SDR:n muoto: I ja Q vuorotellen, etumerkiton 8 bit, 127,5 = 0."""
    lomitettu = np.empty(2 * len(x))
    lomitettu[0::2], lomitettu[1::2] = x.real, x.imag
    koodit = np.clip(np.round(lomitettu / taysi * 127.5 + 127.5), 0, 255)
    koodit.astype(np.uint8).tofile(polku)
# @loppu cu8

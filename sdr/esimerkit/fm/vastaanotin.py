"""FM-stereovastaanotin: kanavan valinta, ilmaisu, pilotti, RDS ja aani."""

from __future__ import annotations

import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from scipy import signal

import rds

Reaali = NDArray[np.float64]
Kompleksi = NDArray[np.complex128]

FS_AANI = 48_000.0


# @alku lue
def lue_cu8(polku: Path) -> Kompleksi:
    """Lukee RTL-SDR:n cu8-tiedoston kompleksiluvuiksi valilla -1...1."""
    raaka = np.fromfile(polku, dtype=np.uint8).astype(np.float64)
    x = (raaka - 127.5) / 127.5
    z: Kompleksi = x[0::2] + 1j * x[1::2]
    return z
# @loppu lue


# @alku kanava
def valitse_kanava(z: Kompleksi, fs: float, keskitaajuus: float,
                   desimointi: int) -> Kompleksi:
    """Siirto nollataajuudelle, 100 kHz:n alipaasto ja desimointi."""
    n = np.arange(len(z))
    siirretty = z * np.exp(-2j * np.pi * keskitaajuus * n / fs)
    h = signal.firwin(129, 100e3, fs=fs)
    y: Kompleksi = signal.upfirdn(h, siirretty, down=desimointi)
    return y[len(h) // (2 * desimointi):]     # suotimen viive pois
# @loppu kanava


# @alku ilmaisin
def fm_ilmaisin(z: Kompleksi, fs: float, poikkeama: float) -> Reaali:
    """Polaari-ilmaisin: perakkaisten naytteiden vaihe-ero."""
    ero = np.angle(z[1:] * np.conj(z[:-1]))
    m: Reaali = ero * fs / (2 * np.pi * poikkeama)
    return m
# @loppu ilmaisin


# @alku jalkikorostus
def jalkikorostus(fs: float, tau: float = 50e-6) -> tuple[Reaali, Reaali]:
    """Ensimmaisen kertaluvun alipaasto 1 / (1 + s tau) bilineaarisena."""
    b, a = signal.bilinear([1.0], [tau, 1.0], fs)
    return b, a
# @loppu jalkikorostus


# @alku pll
@dataclass
class Pll:
    """Toisen kertaluvun vaihelukko, joka ajetaan pienella naytetaajuudella.

    Pilotti suodatetaan kaistanpaastolla, siirretaan nimellistaajuudelta
    nollaan ja desimoidaan; silmukka seuraa jaljelle jaavaa vaihetta.
    """

    kaista_hz: float = 20.0          # silmukan kaistanleveys
    vaimennus: float = 0.707

    def lukitse(self, m: Reaali, fs: float, f0: float,
                desimointi: int) -> tuple[Reaali, float]:
        """Palauttaa pilotin vaiheen MPX:n naytteittain ja taajuusvirheen."""
        n = np.arange(len(m))
        kanta = m * np.exp(-2j * np.pi * f0 * n / fs)   # pilotti -> 0 Hz
        h = signal.firwin(511, 1_500.0, fs=fs)          # aani ja muut pois
        pieni = signal.upfirdn(h, kanta, down=desimointi)
        pieni = pieni[:len(m) // desimointi]
        fs2 = fs / desimointi
        wn = 2 * np.pi * self.kaista_hz / fs2
        kp, ki = 2 * self.vaimennus * wn, wn * wn
        theta, integ = 0.0, 0.0
        vaiheet = np.empty(len(pieni))
        for k, z in enumerate(pieni):
            virhe = float(np.angle(z * np.exp(-1j * theta)))
            integ += ki * virhe
            theta += kp * virhe + integ
            vaiheet[k] = theta
        virhe_hz = integ * fs2 / (2 * np.pi)
        # Suodin viivastaa vaihetta len(h) // 2 naytetta: korjataan.
        vaiheet += 2 * np.pi * virhe_hz * (len(h) // 2) / fs
        theta_mpx = np.interp(n / desimointi, np.arange(len(vaiheet)),
                              vaiheet)
        vaihe: Reaali = 2 * np.pi * f0 * n / fs + theta_mpx
        return vaihe, virhe_hz
# @loppu pll


@dataclass
class Aani:
    vasen: Reaali
    oikea: Reaali


# @alku stereo
def stereo(m: Reaali, phi: Reaali, fs: float,
           korjaa_sinc: bool = True) -> Aani:
    """Summa ja erotus samalla suotimella, jotta viiveet tasmaavat."""
    h = signal.firwin(255, 15_000.0, fs=fs)
    summa = signal.lfilter(h, [1.0], m)
    erotus = 2 * signal.lfilter(h, [1.0], m * np.cos(2 * phi))
    # Vaihe-ero on taajuuden keskiarvo naytevalilla: vaste sinc(f / fs)
    # vaimentaa 38 kHz:n erotuskanavaa. Korjaamaton ero vuotaa kanavasta
    # toiseen (luku 6).
    if korjaa_sinc:
        erotus /= np.sinc(2 * 19_000.0 / fs)
    b, a = jalkikorostus(FS_AANI)

    def aaneksi(x: Reaali) -> Reaali:
        y = signal.resample_poly(x, 4, 19)       # 228 kHz -> 48 kHz
        tulos: Reaali = signal.lfilter(b, a, y) / 0.9
        return tulos

    return Aani(aaneksi(summa + erotus), aaneksi(summa - erotus))
# @loppu stereo


# @alku rdspura
def rds_bitit(m: Reaali, phi: Reaali, fs: float) -> list[int]:
    """57 kHz:n BPSK kantataajuudelle, 4 naytetta bittia kohti ja paatos."""
    h = signal.firwin(511, 2_400.0, fs=fs)
    desimointi = round(fs / (4 * 1187.5))        # 228 kHz -> 4750 Hz
    kanta = signal.upfirdn(h, m * np.cos(3 * phi), down=desimointi)
    # Sovitettu suodin on aikakaannetty bittipulssi (+ + - -).
    sovitettu = np.convolve(kanta, [-1.0, -1.0, 1.0, 1.0], "valid")
    # Bittiajoitus: neljasta vaiheesta se, jossa paatokset ovat varmimpia.
    vaihe = int(np.argmax([np.abs(sovitettu[k::4]).sum() for k in range(4)]))
    d = (sovitettu[vaihe::4] > 0).astype(int)
    return list(np.bitwise_xor(d[1:], d[:-1]))   # differentiaalipurku
# @loppu rdspura


def sinad(x: Reaali, fs: float, taajuus: float) -> tuple[float, float]:
    """Testiaanen amplitudi ja SINAD (aani / kaikki muu) desibeleina."""
    x = x[len(x) // 4:]                          # alkutransientti pois
    ikkuna = signal.windows.blackmanharris(len(x))
    X = np.abs(np.fft.rfft(x * ikkuna)) ** 2
    f = np.fft.rfftfreq(len(x), 1 / fs)
    aani = np.abs(f - taajuus) < 20
    muu = (f > 50) & (f < 15_000) & ~aani
    # Parseval: aanen teho jakautuu ikkunan paakeilaan.
    amplitudi = 2 * np.sqrt(X[aani].sum() / (len(x) * (ikkuna**2).sum()))
    return float(amplitudi), float(10 * np.log10(X[aani].sum()
                                                 / X[muu].sum()))


# @alku wav
def kirjoita_wav(polku: Path, aani: Aani) -> None:
    """16-bittinen stereo-WAV standardikirjaston wave-moduulilla."""
    lr = np.stack([aani.vasen, aani.oikea], axis=1)
    pcm = np.clip(np.round(lr * 32767), -32768, 32767).astype("<i2")
    with wave.open(str(polku), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(int(FS_AANI))
        w.writeframes(pcm.tobytes())
# @loppu wav


# @alku vastaanota
def vastaanota(z: Kompleksi, fs: float, keskitaajuus: float,
               poikkeama: float) -> tuple[Aani, rds.Tulos, float]:
    """Koko ketju tallenteesta aaneen ja asemanimeen."""
    kanava = valitse_kanava(z, fs, keskitaajuus, 4)
    fs_mpx = fs / 4
    m = fm_ilmaisin(kanava, fs_mpx, poikkeama)
    phi, virhe_hz = Pll().lukitse(m, fs_mpx, 19_000.0, 19)
    return stereo(m, phi, fs_mpx), rds.pura(rds_bitit(m, phi, fs_mpx)), \
        virhe_hz
# @loppu vastaanota

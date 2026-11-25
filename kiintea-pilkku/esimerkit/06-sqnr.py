"""Kvantisointikohina: SQNR kasvaa noin 6,02 dB jokaista bittiä kohti."""

import numpy as np
import numpy.typing as npt

Liuku = npt.NDArray[np.float64]


# @alku kvantisointi
def kvantisoi(x: Liuku, bitit: int) -> Liuku:
    """Pyöristys bitit-leveään Q1.(bitit-1)-muotoon saturoiden."""
    skaala = float(1 << (bitit - 1))
    koodi = np.clip(np.round(x * skaala), -skaala, skaala - 1)
    return np.asarray(koodi / skaala, dtype=np.float64)


def sqnr_db(x: Liuku, xq: Liuku) -> float:
    kohina = xq - x
    return float(10 * np.log10(np.mean(x**2) / np.mean(kohina**2)))
# @loppu kvantisointi


# @alku mittaus
# Täyden skaalan siniaalto; taajuus ei ole näytteenottotaajuuden
# rationaalinen osa, joten kohina on tasaista eikä toistu jaksollisena.
n = np.arange(1 << 16)
sini = 0.999 * np.sin(2 * np.pi * 0.1234567 * n)
print(f"{'bitit':>5} {'mitattu (dB)':>13} {'6,02b + 1,76':>13}")
for bitit in (4, 6, 8, 10, 12, 14, 16):
    mitattu = sqnr_db(sini, kvantisoi(sini, bitit))
    print(f"{bitit:>5} {mitattu:>13.2f} {6.02 * bitit + 1.76:>13.2f}")
# @loppu mittaus

# @alku hiljainen
# Sama 16-bittinen muoto, mutta signaali 40 dB alempana: SQNR putoaa
# 40 dB. Kiinteän pilkun tarkkuus on absoluuttinen, ei suhteellinen.
hiljainen = 0.01 * sini
print(f"16 bittiä, signaali -40 dB: "
      f"{sqnr_db(hiljainen, kvantisoi(hiljainen, 16)):.2f} dB")
# @loppu hiljainen


# @alku dither
def kohina(maara: int) -> Liuku:
    """Tasajakautunut [0, 1): oma kongruenssigeneraattori, jotta tulos
    on sama joka ajolla ja joka koneella."""
    tila, arvot = 12345, []
    for _ in range(maara):
        tila = (tila * 1103515245 + 12345) % (1 << 32)
        arvot.append((tila >> 8) / (1 << 24))
    return np.asarray(arvot, dtype=np.float64)


def suurin_piikki_dbc(x: Liuku) -> float:
    """Suurin spektripiikki signaalin ulkopuolella suhteessa signaaliin."""
    spektri = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    huippu = int(np.argmax(spektri))
    muut = np.concatenate([spektri[:huippu - 3], spektri[huippu + 4:]])
    return float(20 * np.log10(np.max(muut) / spektri[huippu]))


# Neljä bittiä: ilman ditheriä virhe on säröpiikkejä. Kolmiojakautunut
# dither (kahden tasajakautuneen summa, +-1 LSB) tekee siitä kohinaa:
# SQNR heikkenee, mutta suurin yksittäinen piikki putoaa.
lsb = 2.0**-3
tpdf = (kohina(2 * len(n)).reshape(2, -1).sum(axis=0) - 1.0) * lsb
puoli = 0.5 * sini                       # tilaa ditherille, ei saturoidu
for nimi, x in (("ilman ditheriä", puoli), ("dither", puoli + tpdf)):
    xq = kvantisoi(x, 4)
    print(f"4 bittiä, {nimi:14}: SQNR {sqnr_db(puoli, xq):5.2f} dB, "
          f"suurin piikki {suurin_piikki_dbc(xq):6.1f} dBc")
# @loppu dither

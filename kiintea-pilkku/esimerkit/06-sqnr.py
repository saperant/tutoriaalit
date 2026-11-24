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

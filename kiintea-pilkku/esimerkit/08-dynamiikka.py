"""Dynamiikka-alue: kiinteä pilkku, liukuluvut ja lohkoliukuluku."""

import math

import numpy as np
import numpy.typing as npt

Liuku = npt.NDArray[np.float64]


# @alku alueet
def db(suhde: float) -> float:
    return 20 * math.log10(suhde)


# Dynamiikka-alue: suurimman ja pienimmän nollasta eroavan arvon suhde.
muodot = [
    ("Q1.15", 1 - 2**-15, 2**-15),
    ("Q1.31", 1 - 2**-31, 2**-31),
    ("binary16", 65504.0, 2**-24),
    ("bfloat16", 3.39e38, 2**-133),
    ("binary32", 3.40e38, 2**-149),
]
for nimi, suurin, pienin in muodot:
    print(f"{nimi:9} {db(suurin / pienin):7.0f} dB")
# @loppu alueet


# @alku lohko
def q15(x: Liuku) -> Liuku:
    return np.asarray(np.clip(np.round(x * 32768), -32768, 32767) / 32768,
                      dtype=np.float64)


def lohkoliukuluku(x: Liuku, lohko: int) -> Liuku:
    """Lohkon näytteillä yhteinen eksponentti: lohkon suurin arvo
    skaalataan välille [0,5, 1) ennen Q1.15-kvantisointia."""
    tulos = np.empty_like(x)
    for alku in range(0, len(x), lohko):
        osa = x[alku:alku + lohko]
        suurin = float(np.max(np.abs(osa)))
        eks = math.floor(math.log2(suurin)) + 1 if suurin > 0 else 0
        tulos[alku:alku + lohko] = q15(osa / 2.0**eks) * 2.0**eks
    return tulos
# @loppu lohko


def sqnr(x: Liuku, xq: Liuku) -> float:
    return float(10 * np.log10(np.mean(x**2) / np.mean((xq - x) ** 2)))


# @alku vertailu
n = np.arange(4096)
print(f"{'taso':>8} {'Q1.15 (dB)':>11} {'lohko 64 (dB)':>14}")
for taso_db in (0, -20, -40, -60):
    x = 0.9 * 10 ** (taso_db / 20) * np.sin(2 * np.pi * 0.0123457 * n)
    print(f"{taso_db:>5} dB {sqnr(x, q15(x)):>11.1f} "
          f"{sqnr(x, lohkoliukuluku(x, 64)):>14.1f}")
# @loppu vertailu

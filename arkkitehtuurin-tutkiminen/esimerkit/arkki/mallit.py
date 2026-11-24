"""Analyyttiset suorituskykymallit.

Amdahlin ja Gustafsonin lait, Hillin ja Martyn moniydinmallit,
roofline usealla muistitasolla, Littlen lakiin perustuva kaistamalli ja
CPI-pino.
"""

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass


# @alku amdahl
def amdahl(p: float, s: float) -> float:
    """Nopeutus, kun osuus p ajosta nopeutuu s-kertaiseksi."""
    return 1 / ((1 - p) + p / s)


def gustafson(p: float, n: int) -> float:
    """Skaalattu nopeutus: rinnakkainen osuus p kasvaa n ytimen mukana."""
    return (1 - p) + p * n
# @loppu amdahl


# @alku hill-marty
def pollack(r: float) -> float:
    """Ytimen suorituskyky r perusytimen (BCE) pinta-alalla
    Pollackin säännön mukaan: sqrt(r)."""
    return math.sqrt(r)


def symmetrinen(f: float, n: float, r: float,
                perf: Callable[[float], float] = pollack) -> float:
    """n BCE:n siru, jossa n/r samanlaista r BCE:n ydintä."""
    return 1 / ((1 - f) / perf(r) + f * r / (perf(r) * n))


def epasymmetrinen(f: float, n: float, r: float,
                   perf: Callable[[float], float] = pollack) -> float:
    """Yksi r BCE:n ydin ja n - r yhden BCE:n ydintä. Sarjaosa ajetaan
    suurella ytimellä, rinnakkaisosa kaikilla yhtä aikaa."""
    return 1 / ((1 - f) / perf(r) + f / (perf(r) + n - r))


def dynaaminen(f: float, n: float, r: float,
               perf: Callable[[float], float] = pollack) -> float:
    """r BCE:tä yhdistyy sarjaosan ajaksi yhdeksi ytimeksi; rinnakkaisosa
    käyttää kaikkia n BCE:tä pieninä ytiminä."""
    return 1 / ((1 - f) / perf(r) + f / n)
# @loppu hill-marty


# @alku roofline
@dataclass(frozen=True)
class Taso:
    nimi: str
    kaista: float  # GB/s
    intensiteetti: float  # FLOP/B tällä tasolla


def roofline(huippu: float, tasot: list[Taso]) -> tuple[float, str]:
    """Saavutettava GFLOP/s ja rajoittava tekijä: laskentakatto tai
    se muistitaso, jonka katto (kaista * intensiteetti) on matalin."""
    paras, raja = huippu, "laskenta"
    for t in tasot:
        katto = t.kaista * t.intensiteetti
        if katto < paras:
            paras, raja = katto, t.nimi
    return paras, raja
# @loppu roofline


# @alku kaista
def littlen_kaista(kesken: float, rivikoko: int, viive_ns: float) -> float:
    """Saavutettava kaista (GB/s), kun keskeneräisiä hutipyyntöjä on
    keskimäärin kesken ja yhden pyynnön viive on viive_ns:
    Littlen laki L = lambda * W, eli lambda = L / W."""
    return kesken * rivikoko / viive_ns


def tarvittava_rinnakkaisuus(kaista: float, rivikoko: int,
                             viive_ns: float) -> float:
    """Kuinka monta pyyntöä on oltava kesken, jotta kaista täyttyy."""
    return kaista * viive_ns / rivikoko
# @loppu kaista


# @alku cpi
def cpi_pino(perus: float, hudit_per_kaskykilo: Mapping[str, float],
             sakot: Mapping[str, float]) -> dict[str, float]:
    """CPI-pino: perus-CPI ja kunkin tason hutien osuus. Hutit ovat
    tuhatta käskyä kohden (MPKI), sakko jaksoina. Malli olettaa, ettei
    hutien viiveitä limitetä keskenään (luku 6 korjaa tämän)."""
    pino = {"perus": perus}
    for taso, mpki in hudit_per_kaskykilo.items():
        pino[taso] = mpki / 1000 * sakot[taso]
    return pino
# @loppu cpi

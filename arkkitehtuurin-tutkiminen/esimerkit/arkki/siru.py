"""Moniydinsirun analyyttinen malli suunnittelutilan tutkimiseen.

Parametrit: r (ytimen koko perusytiminä, BCE), c (yhteinen
välimuisti, MiB) ja v (käyttöjännite, V). Malli yhdistää Hillin ja
Martyn symmetrisen sirun (luku 3), CPI-pinon ja kaistarajan (luku 3)
sekä teho- ja pinta-alamallit (luku 8).
"""

import math
from dataclasses import dataclass

from arkki.teho import Piiri


@dataclass(frozen=True)
class Kuorma:
    rinnakkainen: float = 0.99  # rinnakkaistuva osuus (f)
    mpki: float = 3.0  # hutia / 1000 käskyä 1 MiB:n osuudella
    viive_ns: float = 80.0  # muistiviive
    kaista: float = 25.0  # GB/s


@dataclass(frozen=True)
class Tulos:
    ytimia: int
    nopeutus: float  # perusytimeen (1 BCE, 1 V, 1 MiB) verrattuna
    kaskyja_ns: float  # sama absoluuttisena: käskyä nanosekunnissa
    teho: float  # W rinnakkaisosan aikana
    ala: float  # BCE


# @alku siru
ALA = 64.0  # sirun pinta-ala BCE:inä
VALIMUISTI_ALA = 1.0  # BCE / MiB
VUOTO_VALIMUISTI = 0.5  # W / MiB


def ydin(r: float) -> Piiri:
    """Ytimen sähköiset parametrit kasvavat pinta-alan mukana."""
    return Piiri(kapasitanssi_nf=5.0 * r, vuoto_a=0.3 * r)


def kaskyja_ns(r: float, osuus_mib: float, v: float, k: Kuorma) -> float:
    """Yhden ytimen suoritusnopeus (käskyä / ns): CPI-pino, jossa
    perus-CPI on 1 / sqrt(r) (Pollack) ja hutit neliöjuurisäännöllä."""
    f = ydin(r).taajuus(v)
    mpki = k.mpki / math.sqrt(osuus_mib)
    cpi = 1 / math.sqrt(r) + mpki / 1000 * k.viive_ns * f
    return f / cpi


def arvioi(r: float, c: float, v: float, k: Kuorma | None = None
           ) -> Tulos:
    k = k or Kuorma()
    n = int((ALA - VALIMUISTI_ALA * c) // r)
    if n < 1:
        raise ValueError("ytimet eivät mahdu sirulle")
    sarja = kaskyja_ns(r, c, v, k)  # yksi ydin, koko välimuisti
    rinnakkain = n * kaskyja_ns(r, c / n, v, k)
    # Kaistaraja: hutien tavut eivät voi ylittää muistin kaistaa.
    tarve = rinnakkain * k.mpki / math.sqrt(c / n) / 1000 * 64  # GB/s
    rinnakkain *= min(1.0, k.kaista / tarve)
    aika = (1 - k.rinnakkainen) / sarja + k.rinnakkainen / rinnakkain
    perus = kaskyja_ns(1, 1, 1.0, k)
    p = ydin(r)
    teho = n * (p.dynaaminen(v, p.taajuus(v)) + p.vuoto(v)) \
        + VUOTO_VALIMUISTI * c
    return Tulos(n, 1 / (aika * perus), 1 / aika, teho,
                 n * r + VALIMUISTI_ALA * c)
# @loppu siru

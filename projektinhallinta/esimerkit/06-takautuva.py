"""Takautuva testi: pitävätkö ennusteen varmuustasot paikkansa?

Tuotetaan pitkä keinotekoinen läpäisyhistoria, tehdään joka viides
viikko ennuste 40 työn valmistumisesta edeltävän 20 viikon perusteella ja
katsotaan, kuinka usein työt todella valmistuivat luvattuun viikkoon
mennessä. Hyvin kalibroitu 85 %:n ennuste pitää noin 85 % kerroista.
"""

import math
import random
from collections.abc import Callable

from ennuste import persentiili, valmistumisennuste

IKKUNA, TOITA = 20, 40


def poisson(rng: random.Random, odotus: float) -> int:
    """Poisson-jakautunut satunnaisluku (Knuthin menetelmä)."""
    raja, k, tulo = math.exp(-odotus), 0, rng.random()
    while tulo > raja:
        k += 1
        tulo *= rng.random()
    return k


# @alku testi
def takautuva_testi(lapaisyt: list[int]) -> dict[str, float]:
    """Osuus ennusteista, joihin mennessä työt todella valmistuivat."""
    osumat = {"keskiarvo": 0, "50 %": 0, "85 %": 0, "95 %": 0}
    kertoja = 0
    for nyt in range(IKKUNA, len(lapaisyt) - 40, 5):
        historia = lapaisyt[nyt - IKKUNA:nyt]
        toteuma, jaljella = 0, TOITA          # mitä todella tapahtui
        while jaljella > 0:
            jaljella -= lapaisyt[nyt + toteuma]
            toteuma += 1
        jakauma = valmistumisennuste(historia, TOITA, siemen=nyt,
                                     toistoja=400)
        ennusteet = {
            "keskiarvo": TOITA / (sum(historia) / IKKUNA),
            "50 %": persentiili(jakauma, 0.50),
            "85 %": persentiili(jakauma, 0.85),
            "95 %": persentiili(jakauma, 0.95),
        }
        for nimi, ennuste in ennusteet.items():
            osumat[nimi] += toteuma <= ennuste
        kertoja += 1
    return {nimi: n / kertoja for nimi, n in osumat.items()}
# @loppu testi


def historia(odotus: Callable[[int], float], siemen: int) -> list[int]:
    rng = random.Random(siemen)
    return [poisson(rng, odotus(viikko)) for viikko in range(1500)]


# @alku prosessit
PROSESSIT: dict[str, Callable[[int], float]] = {
    "vakaa tiimi": lambda viikko: 4.0,
    # Tiimistä lähtee kolmannes väestä vuoden välein puoleksi vuodeksi.
    "muuttuva tiimi": lambda viikko: 4.0 if viikko % 52 < 26 else 2.7,
}
# @loppu prosessit

print(f"{'prosessi':<16}" + "".join(f"{n:>11}" for n in
                                    ("keskiarvo", "50 %", "85 %", "95 %")))
for nimi, odotus in PROSESSIT.items():
    tulos = takautuva_testi(historia(odotus, siemen=4))
    print(f"{nimi:<16}" + "".join(f"{osuus:>11.0%}"
                                  for osuus in tulos.values()))

"""Tarinapisteet vai kappalemäärä: kumpi ennustaa paremmin?

Tiimi tekee töitä, joiden todellinen työmäärä vaihtelee. Jäljellä
olevien 60 työn kesto ennustetaan kahdella tavalla 20 viikon historiasta:
pisteet/nopeus ja kappaleet/läpäisy. Kolme tilannetta kertoo, milloin
arvioista on hyötyä.
"""

import random
import statistics

PISTEET = (1, 2, 3, 5, 8)
KAPASITEETTI = 20.0      # työyksikköä viikossa
HAJONTA = 0.6            # todellisen työmäärän logaritminen hajonta
Tyo = tuple[int, float]  # (arvioidut pisteet, todellinen työmäärä)


# @alku tyot
def tyo(rng: random.Random, koot: tuple[int, ...],
        arvio_osuu: bool) -> Tyo:
    """Työ, jonka todellinen työmäärä hajoaa kokonsa ympärille."""
    koko = rng.choice(koot)
    tyomaara = koko * rng.lognormvariate(0, HAJONTA)
    # Jos arviot eivät osu, pisteet arvotaan työmäärästä riippumatta.
    return (koko if arvio_osuu else rng.choice(PISTEET), tyomaara)
# @loppu tyot


# @alku koe
def ennustevirheet(jaljella_koot: tuple[int, ...], arvio_osuu: bool,
                   toistoja: int = 3000) -> tuple[float, float]:
    """Itseisvirheen mediaani pisteillä ja kappalemäärällä."""
    rng = random.Random(21)
    pisteilla, kappaleilla = [], []
    for _ in range(toistoja):
        tehty: list[Tyo] = []
        kaytetty = 0.0
        while kaytetty < 20 * KAPASITEETTI:              # 20 vk historia
            tehty.append(tyo(rng, PISTEET, arvio_osuu))
            kaytetty += tehty[-1][1]
        nopeus = sum(p for p, _ in tehty) / 20           # pistettä/vk
        lapaisy = len(tehty) / 20                        # työtä/vk
        jono = [tyo(rng, jaljella_koot, arvio_osuu) for _ in range(60)]
        toteuma = sum(m for _, m in jono) / KAPASITEETTI
        pisteilla.append(abs(sum(p for p, _ in jono) / nopeus / toteuma - 1))
        kappaleilla.append(abs(len(jono) / lapaisy / toteuma - 1))
    return statistics.median(pisteilla), statistics.median(kappaleilla)
# @loppu koe


TILANTEET = [
    ("sama työjakauma, arviot osuvat", PISTEET, True),
    ("jäljellä vain suuria, arviot osuvat", (5, 8), True),
    ("jäljellä vain suuria, arviot eivät osu", (5, 8), False),
]
print(f"{'tilanne':<40}{'pisteet':>9}{'kappaleet':>11}")
for nimi, koot, osuu in TILANTEET:
    p, k = ennustevirheet(koot, osuu)
    print(f"{nimi:<40}{p:>9.0%}{k:>11.0%}")

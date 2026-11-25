"""Monte Carlo -ennuste läpäisyhistoriasta. Muut esimerkit tuovat tämän.

Ennuste ei tarvitse arvioita yksittäisten töiden koosta. Se olettaa
vain, että tulevat viikot muistuttavat historian viikkoja: jokaiselle
tulevalle viikolle arvotaan läpäisy historiasta.
"""

import random

# Valmistuneita töitä viikossa, viimeiset 20 viikkoa.
HISTORIA = [3, 5, 2, 6, 4, 0, 5, 7, 3, 4, 6, 2, 5, 4, 8, 3, 1, 5, 6, 4]


# @alku ennuste
def viikkoja_tarvitaan(historia: list[int], toita: int,
                       rng: random.Random) -> int:
    """Yksi mahdollinen tulevaisuus: montako viikkoa töihin kuluu."""
    viikot = 0
    while toita > 0:
        toita -= rng.choice(historia)
        viikot += 1
    return viikot


def valmistumisennuste(historia: list[int], toita: int, siemen: int = 1,
                       toistoja: int = 10_000) -> list[int]:
    """Viikkomäärät järjestettyinä: jakauma, ei yksi luku."""
    rng = random.Random(siemen)
    return sorted(viikkoja_tarvitaan(historia, toita, rng)
                  for _ in range(toistoja))


def maaraennuste(historia: list[int], viikkoja: int, siemen: int = 1,
                 toistoja: int = 10_000) -> list[int]:
    """Montako työtä valmistuu annetussa ajassa, järjestettynä."""
    rng = random.Random(siemen)
    return sorted(sum(rng.choice(historia) for _ in range(viikkoja))
                  for _ in range(toistoja))


def persentiili(jarjestetty: list[int], osuus: float) -> int:
    """Pienin arvo, jonka alle tai tasalle jää osuus tuloksista."""
    return jarjestetty[min(len(jarjestetty) - 1,
                           int(osuus * len(jarjestetty)))]
# @loppu ennuste


if __name__ == "__main__":
    # Tarkistus: yhden työn viikossa valmistava tiimi tarvitsee
    # kymmeneen työhön aina kymmenen viikkoa.
    tasainen = valmistumisennuste([1], 10, toistoja=100)
    print("tasainen läpäisy:", tasainen[0], tasainen[-1])
    print("historian keskiarvo:", sum(HISTORIA) / len(HISTORIA))

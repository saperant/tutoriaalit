"""Stokastinen pyöristys: määritelmä, harhattomuus ja virheen kasvu."""

import math
import random
from collections.abc import Callable

Pyoristys = Callable[[float], float]


# @alku maaritelma
def stokastinen(x: float, askel: float, rng: random.Random) -> float:
    """Pyöristää x:n askeleen monikertaan: ylös todennäköisyydellä,
    joka on etäisyys alempaan naapuriin suhteessa askeleeseen."""
    alempi = math.floor(x / askel)
    osuus = x / askel - alempi            # 0 <= osuus < 1
    return (alempi + (rng.random() < osuus)) * askel
# @loppu maaritelma


def lahimpaan(x: float, askel: float) -> float:
    """Pyöristys lähimpään, tasapelit parilliseen."""
    return round(x / askel) * askel


# @alku harhaton
rng = random.Random(2026)                 # kiinteä siemen: toistettava
N = 100_000
print("arvo  lähimpään  stokastisen keskiarvo  hajonta  teoria")
for x in (0.3, 2.5, -1.9, 7.0):
    otos = [stokastinen(x, 1.0, rng) for _ in range(N)]
    keskiarvo = sum(otos) / N
    hajonta = math.sqrt(sum((v - keskiarvo) ** 2 for v in otos) / N)
    p = x - math.floor(x)
    print(f"{x:4.1f} {lahimpaan(x, 1.0):10.0f} {keskiarvo:22.3f} "
          f"{hajonta:8.3f} {math.sqrt(p * (1 - p)):7.3f}")
# @loppu harhaton


# @alku kasvu
def kertyma(n: int, lisays: float, pyorista: Pyoristys) -> float:
    """Summa, joka pyöristetään jokaisen lisäyksen jälkeen."""
    summa = 0.0
    for _ in range(n):
        summa = pyorista(summa + lisays)
    return summa


print("     n  lähimpään  stokastinen (rms)  rms / sqrt(n)")
LISAYS, TOISTOT = 0.3, 100                # lisäys on 0,3 askelta
for n in (100, 400, 1600, 6400):
    tarkka = n * LISAYS
    virhe = abs(kertyma(n, LISAYS, lambda s: lahimpaan(s, 1.0)) - tarkka)
    nelio = 0.0
    for _ in range(TOISTOT):
        s = kertyma(n, LISAYS, lambda s: stokastinen(s, 1.0, rng))
        nelio += (s - tarkka) ** 2
    rms = math.sqrt(nelio / TOISTOT)
    print(f"{n:6d} {virhe:10.0f} {rms:18.1f} {rms / math.sqrt(n):14.2f}")
# @loppu kasvu

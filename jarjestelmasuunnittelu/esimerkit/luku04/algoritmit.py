"""Kuormantasausalgoritmit, kun palvelimet eivät ole samanlaisia.

Neljä palvelinta, joista yksi on puolet hitaampi (vanhempi kone tai
naapurin kuormittama virtuaalikone). Yhteinen kapasiteetti on 350
pyyntöä sekunnissa, ja kuorma on 75 % siitä. Jokainen palvelin
käsittelee pyynnöt yksi kerrallaan saapumisjärjestyksessä.
Simulaatio käyttää kiinteää siementä.
"""

import itertools
import random
from collections import deque
from collections.abc import Callable

from jarjestelma.histogrammi import tarkka_kvantiili

NOPEUDET = [1.0, 1.0, 1.0, 0.5]   # palvelimen nopeus suhteessa muihin
PALVELUAIKA = 0.010               # s nopealla palvelimella
KUORMA = 0.75 * sum(NOPEUDET) / PALVELUAIKA
PYYNTOJA = 50_000

type Valitsin = Callable[[list[int]], int]


# @alku valitsimet
def kierto() -> Valitsin:
    seuraava = itertools.cycle(range(len(NOPEUDET)))
    return lambda kesken: next(seuraava)


def painotettu_kierto() -> Valitsin:
    painot = [round(n * 2) for n in NOPEUDET]          # 2, 2, 2, 1
    jarjestys = [i for i, p in enumerate(painot) for _ in range(p)]
    seuraava = itertools.cycle(jarjestys)
    return lambda kesken: next(seuraava)


def satunnainen(s: random.Random) -> Valitsin:
    return lambda kesken: s.randrange(len(kesken))


def vahiten_kesken() -> Valitsin:
    """Least connections: vähiten keskeneräisiä pyyntöjä."""
    return lambda kesken: min(range(len(kesken)), key=kesken.__getitem__)


def kaksi_satunnaista(s: random.Random) -> Valitsin:
    """Power of two choices: arvotaan kaksi ja valitaan vähemmän
    kuormitettu. Ei tarvitse tietää kaikkien palvelinten tilaa."""
    def valitse(kesken: list[int]) -> int:
        a, b = s.sample(range(len(kesken)), 2)
        return a if kesken[a] <= kesken[b] else b
    return valitse
# @loppu valitsimet


def simuloi(valitsin: Valitsin, s: random.Random) -> tuple[float, ...]:
    valmistuu: list[deque[float]] = [deque() for _ in NOPEUDET]
    vapaa = [0.0] * len(NOPEUDET)
    vasteet: list[float] = []
    hitaalle = 0
    nyt = 0.0
    for _ in range(PYYNTOJA):
        nyt += s.expovariate(KUORMA)
        for jono in valmistuu:
            while jono and jono[0] <= nyt:
                jono.popleft()
        i = valitsin([len(j) for j in valmistuu])
        hitaalle += i == len(NOPEUDET) - 1
        kesto = s.expovariate(1 / PALVELUAIKA) / NOPEUDET[i]
        vapaa[i] = max(nyt, vapaa[i]) + kesto
        valmistuu[i].append(vapaa[i])
        vasteet.append(vapaa[i] - nyt)
    return (tarkka_kvantiili(vasteet, 0.5) * 1000,
            tarkka_kvantiili(vasteet, 0.99) * 1000, hitaalle / PYYNTOJA)


def main() -> None:
    print(f"kuorma {KUORMA:.0f}/s, kapasiteetti"
          f" {sum(NOPEUDET) / PALVELUAIKA:.0f}/s")
    print(f"{'algoritmi':<22}{'p50 ms':>8}{'p99 ms':>9}{'hitaalle':>10}")
    strategiat: list[tuple[str, Callable[[random.Random], Valitsin]]] = [
            ("kierto", lambda s: kierto()),
            ("satunnainen", satunnainen),
            ("painotettu kierto", lambda s: painotettu_kierto()),
            ("vähiten kesken", lambda s: vahiten_kesken()),
            ("kaksi satunnaista", kaksi_satunnaista)]
    for nimi, tee in strategiat:
        s = random.Random(42)
        p50, p99, osuus = simuloi(tee(s), s)
        print(f"{nimi:<22}{p50:>8.0f}{p99:>9.0f}{osuus:>10.0%}")


if __name__ == "__main__":
    main()

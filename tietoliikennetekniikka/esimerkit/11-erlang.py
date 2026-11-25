"""Erlang B: estotodennäköisyys, kun jonoa ei ole."""

import heapq

import numpy as np


# @alku erlang
def erlang_b(kuorma: float, kanavia: int) -> float:
    """Todennäköisyys, että kaikki kanavat ovat varattuja. Kuorma on
    erlangeina: saapumisnopeus kertaa keskimääräinen pitoaika."""
    esto = 1.0
    for n in range(1, kanavia + 1):
        esto = kuorma * esto / (n + kuorma * esto)
    return esto
# @loppu erlang


# @alku simulaatio
def simuloi(kuorma: float, kanavia: int, puheluita: int = 200_000) -> float:
    """Puhelut saapuvat Poisson-prosessina ja kestävät keskimäärin
    yhden aikayksikön. Jos kaikki kanavat ovat varattuja, puhelu
    hylätään."""
    rng = np.random.default_rng(31)
    alut = np.cumsum(rng.exponential(1 / kuorma, puheluita))
    kestot = rng.exponential(1.0, puheluita)
    vapautuu: list[float] = []            # keko varattujen loppuajoista
    estetty = 0
    for alku, kesto in zip(alut.tolist(), kestot.tolist(), strict=True):
        while vapautuu and vapautuu[0] <= alku:
            heapq.heappop(vapautuu)
        if len(vapautuu) == kanavia:
            estetty += 1
        else:
            heapq.heappush(vapautuu, alku + kesto)
    return estetty / puheluita
# @loppu simulaatio


def suurin_kuorma(kanavia: int, esto: float) -> float:
    """Suurin kuorma, jolla esto pysyy rajan alla (puolitushaku)."""
    ala, yla = 0.0, float(kanavia)
    for _ in range(50):
        keski = (ala + yla) / 2
        if erlang_b(keski, kanavia) < esto:
            ala = keski
        else:
            yla = keski
    return ala


# @alku vertailu
print("kanavia  kuorma (E)  esto sim  Erlang B")
for kanavia, kuorma in ((30, 20.0), (30, 25.0), (30, 30.0)):
    print(f"{kanavia:>7} {kuorma:>11.0f} {simuloi(kuorma, kanavia):>9.4f}"
          f" {erlang_b(kuorma, kanavia):>9.4f}")
print("kanavia  kuorma 1 %:n estolla  käyttöaste")
for kanavia in (10, 30, 100):
    kuorma = suurin_kuorma(kanavia, 0.01)
    print(f"{kanavia:>7} {kuorma:>20.1f} {kuorma * 0.99 / kanavia:>11.0%}")
# @loppu vertailu

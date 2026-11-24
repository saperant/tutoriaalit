"""Suunnittelutilan tutkiminen: näytteistys, Pareto-rintama ja
herkkyysanalyysi. Parametrit ovat diskreettejä tasoja."""

import random
from collections.abc import Callable, Mapping, Sequence
from itertools import product

Piste = dict[str, float]
Tila = Mapping[str, Sequence[float]]


# @alku naytteistys
def ruudukko(tila: Tila) -> list[Piste]:
    """Täysi faktorikoe: kaikki tasojen yhdistelmät."""
    nimet = list(tila)
    return [dict(zip(nimet, arvot, strict=True))
            for arvot in product(*(tila[n] for n in nimet))]


def satunnainen(tila: Tila, n: int, sat: random.Random) -> list[Piste]:
    """n riippumatonta satunnaista pistettä."""
    return [{nimi: sat.choice(tasot) for nimi, tasot in tila.items()}
            for _ in range(n)]


def latinalainen(tila: Tila, n: int, sat: random.Random) -> list[Piste]:
    """Latinalainen hyperkuutio (McKay ym. 1979): jokaisen parametrin
    vaihteluväli jaetaan n osaan, ja kukin osa saa täsmälleen yhden
    pisteen. Osat sekoitetaan parametreittain toisistaan
    riippumatta."""
    sarakkeet = {}
    for nimi, tasot in tila.items():
        osat = [(i + sat.random()) / n for i in range(n)]
        sat.shuffle(osat)
        sarakkeet[nimi] = [tasot[int(u * len(tasot))] for u in osat]
    return [{nimi: sarakkeet[nimi][i] for nimi in tila} for i in range(n)]
# @loppu naytteistys


# @alku pareto
def dominoi(a: Sequence[float], b: Sequence[float]) -> bool:
    """a dominoi b:tä, jos se on kaikissa tavoitteissa vähintään yhtä
    hyvä ja jossakin parempi. Kaikki tavoitteet minimoidaan."""
    return (all(x <= y for x, y in zip(a, b, strict=True))
            and any(x < y for x, y in zip(a, b, strict=True)))


def pareto(tavoitteet: Sequence[Sequence[float]]) -> list[int]:
    """Niiden pisteiden indeksit, joita mikään muu piste ei dominoi."""
    return [i for i, a in enumerate(tavoitteet)
            if not any(dominoi(b, a) for b in tavoitteet)]
# @loppu pareto


# @alku herkkyys
def herkkyys(malli: Callable[[Piste], float], perus: Piste,
             muutos: float = 0.1) -> dict[str, float]:
    """Joustot: tuloksen suhteellinen muutos jaettuna parametrin
    suhteellisella muutoksella, kun kutakin parametria muutetaan
    yksi kerrallaan +-muutos (keskeisdifferenssi)."""
    y = malli(perus)
    tulos = {}
    for nimi, arvo in perus.items():
        yla = malli({**perus, nimi: arvo * (1 + muutos)})
        ala = malli({**perus, nimi: arvo * (1 - muutos)})
        tulos[nimi] = (yla - ala) / (2 * muutos * y)
    return tulos
# @loppu herkkyys

"""Jonoteoria: avoimet M/M/1-, M/M/c- ja M/G/1-jonot, suljettu
järjestelmä (MVA) ja tapahtumapohjainen jonosimulaattori."""

import heapq
import math
import random
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Jono:
    """Jonon tunnusluvut: käyttöaste, odotus jonossa (Wq), viipymä
    järjestelmässä (W) ja keskimääräinen määrä järjestelmässä (L)."""
    kayttoaste: float
    odotus: float
    viipyma: float
    maara: float


# @alku mm1
def mm1(saapumis: float, palvelu: float) -> Jono:
    """M/M/1: Poisson-saapumiset (lambda), eksponentiaalinen palvelu
    (mu), yksi palvelija. Vakaa vain, kun rho = lambda / mu < 1."""
    rho = saapumis / palvelu
    if rho >= 1:
        raise ValueError("jono ei ole vakaa: käyttöaste >= 1")
    w = 1 / (palvelu - saapumis)
    return Jono(rho, w - 1 / palvelu, w, saapumis * w)  # L = lambda W
# @loppu mm1


# @alku mmc
def erlang_c(c: int, a: float) -> float:
    """Todennäköisyys, että saapuva asiakas joutuu odottamaan, kun
    palvelijoita on c ja tarjottu kuorma on a = lambda / mu."""
    rho = a / c
    summa = sum(a**k / math.factorial(k) for k in range(c))
    viimeinen = a**c / math.factorial(c) / (1 - rho)
    return viimeinen / (summa + viimeinen)


def mmc(saapumis: float, palvelu: float, c: int) -> Jono:
    """M/M/c: c rinnakkaista palvelijaa yhteisellä jonolla."""
    a = saapumis / palvelu
    if a >= c:
        raise ValueError("jono ei ole vakaa: käyttöaste >= 1")
    wq = erlang_c(c, a) / (c * palvelu - saapumis)
    w = wq + 1 / palvelu
    return Jono(a / c, wq, w, saapumis * w)
# @loppu mmc


# @alku mg1
def mg1(saapumis: float, ka: float, toinen_momentti: float) -> Jono:
    """M/G/1 Pollaczekin ja Hinchinin kaavalla: palveluajan
    keskiarvo ka ja toinen momentti E[S^2]. Vakiopalvelulla (M/D/1)
    E[S^2] = ka^2, eksponentiaalisella 2 ka^2."""
    rho = saapumis * ka
    if rho >= 1:
        raise ValueError("jono ei ole vakaa: käyttöaste >= 1")
    wq = saapumis * toinen_momentti / (2 * (1 - rho))
    return Jono(rho, wq, wq + ka, saapumis * (wq + ka))
# @loppu mg1


# @alku mva
def mva(asiakkaat: int, miettimisaika: float, palveluajat: list[float]
        ) -> tuple[float, float]:
    """Suljetun jonoverkon keskiarvoanalyysi (Reiser ja Lavenberg 1980).
    Asiakkaat kiertävät: miettimisaika Z (ei jonoa), sitten jokainen
    palveluasema vuorollaan. Palauttaa läpäisyn X ja vasteajan R
    asemien läpi. Perustuu saapumisteoreemaan: saapuva asiakas näkee
    asemalla keskimäärin yhtä monta kuin verkossa, jossa on yksi
    asiakas vähemmän."""
    jonossa = [0.0] * len(palveluajat)
    x = r = 0.0
    for n in range(1, asiakkaat + 1):
        viipymat = [s * (1 + q) for s, q in zip(palveluajat, jonossa,
                                                strict=True)]
        r = sum(viipymat)
        x = n / (miettimisaika + r)
        jonossa = [x * v for v in viipymat]
    return x, r
# @loppu mva


# @alku simulaattori
@dataclass(frozen=True)
class Mittaus:
    odotus: float
    viipyma: float
    maara: float  # aikakeskiarvo, mitattu erikseen Littlen lain tarkistukseen
    kayttoaste: float


def simuloi(saapumis: float, palveluaika: Callable[[random.Random], float],
            palvelijat: int, asiakkaat: int, siemen: int) -> Mittaus:
    """FCFS-jono, jossa on palvelijat rinnakkaista palvelijaa. Asiakas
    menee palvelijalle, joka vapautuu ensimmäisenä. Ensimmäinen
    kymmenesosa asiakkaista on lämmittelyä, eikä sitä mitata."""
    sat = random.Random(siemen)
    vapaana = [0.0] * palvelijat  # keko: hetket, jolloin vapautuvat
    tapahtumat: list[tuple[float, int]] = []  # (hetki, +1 / -1)
    t = odotus = viipyma = kiireinen = 0.0
    alku = asiakkaat // 10
    for i in range(asiakkaat):
        t += -math.log(1.0 - sat.random()) / saapumis
        s = palveluaika(sat)
        aloitus = max(t, heapq.heappop(vapaana))
        heapq.heappush(vapaana, aloitus + s)
        if i >= alku:
            odotus += aloitus - t
            viipyma += aloitus + s - t
            kiireinen += s
            tapahtumat += [(t, 1), (aloitus + s, -1)]
    mitattu = asiakkaat - alku
    # Määrä järjestelmässä aikakeskiarvona: integroidaan askelfunktio.
    tapahtumat.sort()
    pinta = edellinen = 0.0
    nyt = 0
    for hetki, muutos in tapahtumat:
        pinta += nyt * (hetki - edellinen)
        nyt += muutos
        edellinen = hetki
    kesto = tapahtumat[-1][0] - tapahtumat[0][0]
    return Mittaus(odotus / mitattu, viipyma / mitattu, pinta / kesto,
                   kiireinen / (kesto * palvelijat))
# @loppu simulaattori


def eksponentiaalinen(ka: float) -> Callable[[random.Random], float]:
    """Palveluaika Exp(1 / ka)."""
    return lambda sat: -math.log(1.0 - sat.random()) * ka


def vakio(ka: float) -> Callable[[random.Random], float]:
    """Vakiopalveluaika (M/D/c)."""
    return lambda _sat: ka

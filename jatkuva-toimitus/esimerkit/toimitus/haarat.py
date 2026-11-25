"""Malli: kuinka usein haara törmää runkoon, kun se elää pidempään.

Repositoriossa on tiedostoja ja rivejä. Runkoon tulee joka päivä
muutoksia satunnaisiin riveihin, ja haaran tekijä muuttaa omiaan.
Yhdistäminen on ristiriitainen, jos kumpikin on muuttanut samaa tai
viereistä riviä samassa tiedostossa. Samoin toimii Gitin kolmitieyhdistys.
"""

import random
from dataclasses import dataclass

Rivi = tuple[int, int]      # (tiedosto, rivinumero)


# @alku malli
@dataclass(frozen=True)
class Repo:
    tiedostoja: int = 60
    riveja: int = 100
    runko_paivassa: int = 20     # muutettua riviä päivässä muilta
    haara_paivassa: int = 5      # muutettua riviä päivässä haarassa


def muutokset(arpa: random.Random, repo: Repo, maara: int) -> set[Rivi]:
    return {(arpa.randrange(repo.tiedostoja), arpa.randrange(repo.riveja))
            for _ in range(maara)}


def ristiriidat(runko: set[Rivi], haara: set[Rivi]) -> int:
    """Haaran rivit, joiden kohdalla tai vieressä runko on muuttunut."""
    return sum(1 for tiedosto, rivi in haara
               if any((tiedosto, rivi + ero) in runko for ero in (-1, 0, 1)))


def kokeile(repo: Repo, ika: int, toistoja: int,
            siemen: int = 1) -> tuple[float, float]:
    """Palauttaa ristiriidan todennäköisyyden ja ristiriitojen keskiarvon."""
    arpa = random.Random(siemen)
    osumat = yhteensa = 0
    for _ in range(toistoja):
        runko = muutokset(arpa, repo, repo.runko_paivassa * ika)
        haara = muutokset(arpa, repo, repo.haara_paivassa * ika)
        maara = ristiriidat(runko, haara)
        osumat += maara > 0
        yhteensa += maara
    return osumat / toistoja, yhteensa / toistoja
# @loppu malli

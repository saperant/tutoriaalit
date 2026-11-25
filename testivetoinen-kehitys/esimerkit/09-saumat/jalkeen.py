"""Tilausvahvistus: puhdas ydin ja ohut kuori."""

import random
from dataclasses import dataclass
from datetime import date, datetime, timedelta

MERKIT = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
VIIMEINEN_LAHTOTUNTI = 15
TOIMITUSAIKA = timedelta(days=2)


# @alku ydin
def seuraava_arkipaiva(paiva: date) -> date:
    """Päivä itse, jos se on arkipäivä, muuten seuraava maanantai."""
    while paiva.weekday() >= 5:
        paiva += timedelta(days=1)
    return paiva


def lahtopaiva(tilattu: datetime) -> date:
    paiva = tilattu.date()
    if tilattu.hour >= VIIMEINEN_LAHTOTUNTI:
        paiva += timedelta(days=1)
    return seuraava_arkipaiva(paiva)


def saapumispaiva(lahto: date) -> date:
    return seuraava_arkipaiva(lahto + TOIMITUSAIKA)


def seurantakoodi(arpa: random.Random) -> str:
    return "".join(arpa.choice(MERKIT) for _ in range(6))


@dataclass(frozen=True)
class Vahvistus:
    tilausnumero: int
    lahto: date
    saapuu: date
    koodi: str

    def teksti(self) -> str:
        return (f"Tilaus {self.tilausnumero} lähtee {self.lahto:%d.%m.} ja "
                f"saapuu {self.saapuu:%d.%m.} Seurantakoodi: {self.koodi}")


def vahvista(tilausnumero: int, tilattu: datetime,
             arpa: random.Random) -> Vahvistus:
    lahto = lahtopaiva(tilattu)
    return Vahvistus(tilausnumero, lahto, saapumispaiva(lahto),
                     seurantakoodi(arpa))
# @loppu ydin


# @alku kuori
def vahvista_tilaus(tilausnumero: int) -> None:
    """Kuori: hakee ajan ja satunnaisuuden ja tulostaa tuloksen."""
    vahvistus = vahvista(tilausnumero, datetime.now(),
                         random.SystemRandom())
    print(vahvistus.teksti())
# @loppu kuori

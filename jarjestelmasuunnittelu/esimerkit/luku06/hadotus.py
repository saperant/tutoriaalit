"""Kun välimuisti on täynnä: häätöpolitiikat.

Redisille annetaan 4 Mt muistia, ja 10 000 tuotetta vievät noin
kolminkertaisesti tilaa. Suosio noudattaa Zipfin jakaumaa, ja kesken
ajon suosituimmat tuotteet vaihtuvat (uusi mallisto). Osumasuhde
mitataan vaihdon jälkeen politiikoilla allkeys-lru, allkeys-random ja
noeviction. Redisin LRU on likimääräinen (se vertaa satunnaista
otosta avaimia), joten osumasuhteet vaihtelevat hieman ajosta
toiseen; siksi tulostetaan vain vertailujen tulokset.
"""

import itertools
import random

from jarjestelma.resp import Redis, RedisVirhe
from jarjestelma.ymparisto import Ymparisto

TUOTTEITA = 10_000
ARVO = "x" * 1000


def kuorma(portti: int) -> tuple[float, int]:
    """Palauttaa osumasuhteen vaihdon jälkeen ja epäonnistuneiden
    tallennusten määrän."""
    s = random.Random(3)
    painot = list(itertools.accumulate(1 / i for i in range(1, TUOTTEITA)))
    vanhat = [f"tuote:{i}" for i in range(1, TUOTTEITA)]
    uudet = vanhat[5000:] + vanhat[:5000]     # suosio siirtyy
    pyynnot = s.choices(vanhat, cum_weights=painot, k=20_000) \
        + s.choices(uudet, cum_weights=painot, k=20_000)
    osumia = virheita = 0
    with Redis(portti) as r:
        for i, avain in enumerate(pyynnot):
            if r.komento("GET", avain) is not None:
                osumia += i >= 20_000
                continue
            try:
                r.komento("SET", avain, ARVO)
            except RedisVirhe as virhe:
                virheita += str(virhe).startswith("OOM")
    return osumia / 20_000, virheita


def main() -> None:
    tulokset = {}
    with Ymparisto() as ymp:
        # @alku politiikat
        for politiikka in ("allkeys-lru", "allkeys-random", "noeviction"):
            portti = ymp.redis("--maxmemory", "4mb",
                               "--maxmemory-policy", politiikka)
            tulokset[politiikka] = kuorma(portti)
        # @loppu politiikat
    lru, satunnainen, ei_haatoa = (tulokset[p][0] for p in tulokset)
    print("lru ja random lähes samat (ero < 5 %-yks.):",
          abs(lru - satunnainen) < 0.05)
    print("noeviction yli 30 %-yks. huonompi kuin lru:",
          lru - ei_haatoa > 0.3)
    print("noeviction hylkäsi tallennuksia (OOM):",
          tulokset["noeviction"][1] > 0)
    print("allkeys-lru hylkäsi tallennuksia:", tulokset["allkeys-lru"][1])


if __name__ == "__main__":
    main()

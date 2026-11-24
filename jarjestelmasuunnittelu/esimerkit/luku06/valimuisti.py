"""Cache-aside ja osumasuhde sekä invalidoinnin kilpatilanne.

Tuotteita on 10 000, ja suosio noudattaa Zipfin jakaumaa: muutama
tuote saa suuren osan katseluista. Lopuksi näytetään, miten
invalidoinnin ja hitaan haun lomittuminen jättää muistiin vanhan
hinnan ja miten vuokra estää sen. Lomitus tehdään vaiheittain, jotta
tulos on joka ajolla sama.
"""

import itertools
import random

from jarjestelma.resp import Redis, teksti
from jarjestelma.valimuisti import (
    Tietokanta,
    aloita,
    hae_rinnalta,
    invalidoi,
    tallenna,
)
from jarjestelma.ymparisto import Ymparisto

TUOTTEITA = 10_000


def zipf(n: int, s: float = 1.0) -> list[float]:
    """Kertymäpainot: tuotteen i suosio on verrannollinen 1/i^s."""
    return list(itertools.accumulate(1 / i ** s for i in range(1, n + 1)))


def main() -> None:
    kanta = Tietokanta({f"tuote:{i}": f"{i % 90 + 10}.00"
                        for i in range(TUOTTEITA)})
    with Ymparisto() as ymp, Redis(ymp.redis()) as r:
        # @alku osumat
        s = random.Random(1)
        painot = zipf(TUOTTEITA)
        avaimet = [f"tuote:{i}" for i in range(TUOTTEITA)]
        for kierros, maara in enumerate((2_000, 20_000), 1):
            ennen = kanta.hakuja
            for avain in s.choices(avaimet, cum_weights=painot, k=maara):
                hae_rinnalta(r, kanta, avain)
            haut = kanta.hakuja - ennen
            print(f"kierros {kierros}: {maara} pyyntöä, kantahakuja {haut},"
                  f" osumasuhde {1 - haut / maara:.0%}")
        # @loppu osumat

        # @alku kilpa
        kanta.paivita("tuote:1", "10.00")
        invalidoi(r, "tuote:1")
        # A: huti, hakee kannasta vanhan hinnan (hidas haku alkaa)
        vanha = kanta.hae("tuote:1")
        # B: päivittää hinnan ja invalidoi välimuistin
        kanta.paivita("tuote:1", "12.00")
        invalidoi(r, "tuote:1")
        # A: haku valmistuu, tallentaa vanhan arvon
        r.komento("SET", "tuote:1", vanha, "EX", 3600)
        print("ilman vuokraa muistissa:",
              teksti(r.komento("GET", "tuote:1")))

        invalidoi(r, "tuote:1")
        kanta.paivita("tuote:1", "10.00")
        tunnus = aloita(r, "tuote:1")           # A: huti ja vuokra
        if tunnus is None:
            raise RuntimeError("vuokra oli jo varattu")
        vanha = kanta.hae("tuote:1")
        kanta.paivita("tuote:1", "12.00")       # B: päivitys ...
        invalidoi(r, "tuote:1")                 # ... poistaa vuokran
        print("vuokralla tallennus onnistui:",
              tallenna(r, "tuote:1", tunnus, vanha))
        print("vuokralla seuraava luku:",
              hae_rinnalta(r, kanta, "tuote:1"))
        # @loppu kilpa


if __name__ == "__main__":
    main()

"""Häntälatenssi ja hajautettu kysely (fan-out).

Taustapalvelu vastaa yleensä 5-15 ms:ssa, mutta 1 % kutsuista osuu
hitaaseen hetkeen (roskienkeruu, levy, naapurin kuorma) ja kestää
100-300 ms. Pyyntö, joka kysyy N palvelinta rinnakkain, on yhtä hidas
kuin hitain vastaus. Simulaatio käyttää kiinteää siementä.
"""

import random
from collections.abc import Callable
from functools import partial

from jarjestelma.histogrammi import tarkka_kvantiili

PYYNTOJA = 20_000


# @alku kutsu
def kutsu(satunnainen: random.Random) -> float:
    """Yhden taustakutsun latenssi millisekunteina."""
    if satunnainen.random() < 0.01:
        return satunnainen.uniform(100, 300)
    return satunnainen.uniform(5, 15)


def hajautettu(satunnainen: random.Random, n: int) -> float:
    """Pyyntö odottaa kaikkia n vastausta: latenssi on maksimi."""
    return max(kutsu(satunnainen) for _ in range(n))


def varmistettu(satunnainen: random.Random, n: int, raja: float) -> float:
    """Varmistettu pyyntö (hedged request): jos vastausta ei ole rajan
    jälkeen, sama kysely lähetetään toiselle kopiolle ja käytetään
    nopeampaa. Hinta: noin (1 - p_raja) lisää kutsuja."""
    def yksi() -> float:
        eka = kutsu(satunnainen)
        if eka <= raja:
            return eka
        return min(eka, raja + kutsu(satunnainen))
    return max(yksi() for _ in range(n))
# @loppu kutsu


def tilasto(nimi: str, mittaa: Callable[[], float]) -> None:
    arvot = [mittaa() for _ in range(PYYNTOJA)]
    print(f"{nimi:<26}{tarkka_kvantiili(arvot, 0.5):6.0f}"
          f"{tarkka_kvantiili(arvot, 0.99):7.0f}"
          f"{tarkka_kvantiili(arvot, 0.999):7.0f}")


def main() -> None:
    satunnainen = random.Random(2026)
    print(f"{'pyyntö':<26}{'p50':>6}{'p99':>7}{'p99.9':>7}  (ms)")
    for n in (1, 10, 100):
        tilasto(f"{n} taustakutsua", partial(hajautettu, satunnainen, n))
    for n in (10, 100):
        tilasto(f"{n} kutsua, varmistus 20 ms",
                partial(varmistettu, satunnainen, n, 20))
    print("hitaan osuman todennäköisyys pyyntöä kohden:")
    for n in (1, 10, 100):
        print(f"  {n:>3} kutsua: {1 - 0.99 ** n:5.1%}")


if __name__ == "__main__":
    main()

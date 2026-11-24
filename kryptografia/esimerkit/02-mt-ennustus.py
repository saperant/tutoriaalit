"""Opetusesimerkki: random-moduulin tulosteista voi päätellä tulevat arvot.

Mersenne Twister (MT19937) palauttaa sisäisen tilansa 624 sanaa
sekoitettuina. Sekoitus on kääntyvä, joten 624 peräkkäistä 32-bittistä
tulosta riittää tilan palauttamiseen.
"""

import random

MASKI = 0xFFFFFFFF


# @alku kaanto
def kumoa_oikealle(y: int, siirto: int) -> int:
    """Kumoaa operaation y ^= y >> siirto."""
    tulos = y
    for _ in range(32 // siirto + 1):
        tulos = y ^ (tulos >> siirto)
    return tulos & MASKI


def kumoa_vasemmalle(y: int, siirto: int, maski: int) -> int:
    """Kumoaa operaation y ^= (y << siirto) & maski."""
    tulos = y
    for _ in range(32 // siirto + 1):
        tulos = y ^ ((tulos << siirto) & maski)
    return tulos & MASKI


def palauta_sana(tuloste: int) -> int:
    """Kumoaa MT19937:n sekoituksen (tempering) yhdelle sanalle."""
    y = kumoa_oikealle(tuloste, 18)
    y = kumoa_vasemmalle(y, 15, 0xEFC60000)
    y = kumoa_vasemmalle(y, 7, 0x9D2C5680)
    return kumoa_oikealle(y, 11)
# @loppu kaanto


def main() -> None:
    # Uhri luo "satunnaisia" tunnisteita random-moduulilla.
    uhri = random.Random(20261124)
    havaitut = [uhri.getrandbits(32) for _ in range(624)]

    # @alku ennustus
    tila = [palauta_sana(t) for t in havaitut]
    klooni = random.Random()
    klooni.setstate((3, (*tila, 624), None))

    ennuste = [klooni.getrandbits(32) for _ in range(5)]
    todelliset = [uhri.getrandbits(32) for _ in range(5)]
    print("seuraavat 5 arvoa ennustettiin oikein:", ennuste == todelliset)
    # @loppu ennustus


if __name__ == "__main__":
    main()

"""Muistijälkien analyysin testit."""

import random

from arkki.jalki import (AARETON, etaisyydet, etaisyydet_pino, hutikayra,
                         lru_hudit, tyojoukko)


# @alku esimerkki
def test_kasin_laskettu_esimerkki() -> None:
    # a b a c b a: b:n jälkeen a on 1 rivin päässä, c:n ja a:n
    # jälkeen b 2 rivin päässä, b:n ja c:n jälkeen a 2 rivin päässä.
    assert etaisyydet([1, 2, 1, 3, 2, 1]) == [
        AARETON, AARETON, 1, AARETON, 2, 2]
# @loppu esimerkki


# @alku vertailu
def test_nopea_ja_pino_antavat_saman() -> None:
    sat = random.Random(3)
    rivit = [sat.randrange(50) for _ in range(2000)]
    assert etaisyydet(rivit) == etaisyydet_pino(rivit)


def test_hutikayra_vastaa_simulointia() -> None:
    sat = random.Random(4)
    rivit = [sat.randrange(100) for _ in range(3000)]
    kayra = hutikayra(etaisyydet(rivit), [1, 8, 32, 64])
    for koko, hudit in kayra.items():
        assert hudit == lru_hudit(rivit, koko, koko)
# @loppu vertailu


def test_suora_kuvaus_aiheuttaa_konfliktit() -> None:
    # Rivit 0 ja 4 osuvat samaan joukkoon, kun joukkoja on 4.
    rivit = [0, 4] * 10
    assert lru_hudit(rivit, 4, 1) == 20
    assert lru_hudit(rivit, 4, 4) == 2


def test_tyojoukko() -> None:
    assert tyojoukko([1, 1, 2, 2, 3, 3, 4, 4], 4) == 2.0

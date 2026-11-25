"""Julkaisumallin ominaisuudet, joihin luvun johtopäätökset nojaavat."""

import random

from toimitus.julkaisu import STRATEGIAT, Asetelma, Strategia, simuloi

STRATEGIA = {s.nimi: s for s in STRATEGIAT}


def aja(nimi: str, virhe: float, siemen: int = 5) -> list[int]:
    arpa = random.Random(siemen)
    asetelma = Asetelma(virhe_uusi=virhe)
    return [simuloi(STRATEGIA[nimi], asetelma, arpa).virheita
            for _ in range(100)]


def test_ehja_versio_menee_lapi_joka_strategialla() -> None:
    arpa = random.Random(1)
    for strategia in STRATEGIAT:
        tulos = simuloi(strategia, Asetelma(virhe_uusi=0.0), arpa)
        assert not tulos.peruttu
        assert tulos.askelia == len(strategia.portaat)


def test_rikkinainen_versio_perutaan() -> None:
    arpa = random.Random(2)
    for strategia in STRATEGIAT:
        assert simuloi(strategia, Asetelma(virhe_uusi=0.5), arpa).peruttu


def test_kanarialintu_altistaa_vahiten() -> None:
    keskiarvo = {nimi: sum(aja(nimi, 0.05)) / 100 for nimi in STRATEGIA}
    assert keskiarvo["kanarialintu"] < keskiarvo["rullaava"]
    assert keskiarvo["rullaava"] < keskiarvo["sinivihreä"]
    assert keskiarvo["sinivihreä"] < keskiarvo["kerralla"]


def test_pienesta_naytteesta_ei_paateta() -> None:
    varovainen = Strategia("koe", (0.01, 1.0), ())
    tulos = simuloi(varovainen, Asetelma(virhe_uusi=1.0), random.Random(3))
    assert tulos.askelia == 2            # 10 pyyntöä ei riitä perumiseen

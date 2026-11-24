"""UART-mallin testit: kehys ja vastaanotin."""

import random

import pytest

from mallit.uart import Kehysmuoto, kehyksen_bitit, linja, vastaanota

MUODOT = [Kehysmuoto(), Kehysmuoto(7, "E", 1), Kehysmuoto(8, "O", 2)]


@pytest.mark.parametrize("muoto", MUODOT, ids=str)
def test_kaikki_tavut_kulkevat(muoto: Kehysmuoto) -> None:
    data = bytes(range(2**muoto.databitit))
    saadut = vastaanota(linja(data, muoto), muoto)
    assert [s.tavu for s in saadut] == list(data)
    assert all(s.virhe is None for s in saadut)


def test_kehyksen_rakenne() -> None:
    # 'A' = 0x41 = 0100 0001: START, LSB ensin, parillinen pariteetti
    bitit = kehyksen_bitit(0x41, Kehysmuoto(pariteetti="E"))
    assert bitit == [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1]


@pytest.mark.parametrize("virhe", [-0.04, -0.02, 0.02, 0.05])
def test_sietaa_nopeuseron(virhe: float) -> None:
    satunnainen = random.Random(1)
    data = bytes(satunnainen.randrange(256) for _ in range(50))
    muoto = Kehysmuoto()
    saadut = vastaanota(linja(data, muoto, 16 * (1 + virhe)), muoto)
    assert bytes(s.tavu for s in saadut) == data


def test_liian_suuri_nopeusero_havaitaan() -> None:
    muoto = Kehysmuoto()
    saadut = vastaanota(linja(b"\x00" * 4, muoto, 16 * 0.93), muoto)
    assert any(s.virhe == "kehys" or s.tavu != 0 for s in saadut)


def test_pariteettivirhe() -> None:
    muoto = Kehysmuoto(pariteetti="O")
    naytteet = linja(b"\x0f", muoto)
    alku = naytteet.index(0)
    naytteet[alku + 16 * 2 + 8] ^= 1  # d1:n keskikohta
    assert vastaanota(naytteet, muoto)[0].virhe == "pariteetti"

"""CAN-mallin testit: täyttö, CRC, purku ja arbitraatio."""

import random

import pytest

from mallit.can import (ACK_PAIKKA, Kehys, Taytevirhe, Virhelaskurit,
                        arbitraatio, crc15, lahetettavat, poista_taytto,
                        tayta, vastaanota)


def satunnaiset_kehykset(n: int) -> list[Kehys]:
    s = random.Random(3)
    return [Kehys(s.randrange(0x800), bytes(s.randrange(256) for _ in
                                            range(s.randrange(9))))
            for _ in range(n)]


def test_tayton_kierros_ja_ei_kuutta_samaa() -> None:
    s = random.Random(5)
    for _ in range(200):
        bitit = [s.choice([0, 0, 0, 1]) for _ in range(s.randrange(80))]
        taytetty, _ = tayta(bitit)
        teksti = "".join(map(str, taytetty))
        assert "000000" not in teksti and "111111" not in teksti
        assert poista_taytto(taytetty) == bitit


def test_kuusi_samaa_on_taytevirhe() -> None:
    with pytest.raises(Taytevirhe):
        poista_taytto([0] * 6)


def test_crc_jaannos_nolla() -> None:
    # Viestin ja sen CRC:n yhdistelmän CRC on nolla.
    for kehys in satunnaiset_kehykset(50):
        alue = [b for _, k in kehys.kentat() for b in k]
        assert crc15(alue) == 0


def test_kehysten_kierros() -> None:
    for kehys in satunnaiset_kehykset(100):
        linja = lahetettavat(kehys)
        linja[ACK_PAIKKA] = 0
        assert vastaanota(linja) == kehys


def test_yksittainen_bittivirhe_havaitaan() -> None:
    kehys = Kehys(0x2A5, bytes(range(8)))
    linja = lahetettavat(kehys)
    for kohta in range(len(linja) - 10):
        vaurio = list(linja)
        vaurio[kohta] ^= 1
        with pytest.raises(ValueError):
            vastaanota(vaurio)


def test_arbitraatio_pienin_voittaa() -> None:
    kehykset = satunnaiset_kehykset(6)
    tunnisteet = [k.tunniste for k in kehykset]
    assert len(set(tunnisteet)) == len(tunnisteet)
    tulos = arbitraatio(kehykset)
    assert tunnisteet[tulos.voittaja] == min(tunnisteet)
    assert tulos.vayla == lahetettavat(kehykset[tulos.voittaja])


def test_bus_off_32_virheen_jalkeen() -> None:
    solmu = Virhelaskurit()
    for _ in range(31):
        solmu.lahetysvirhe()
    assert solmu.tila == "error passive"
    solmu.lahetysvirhe()
    assert solmu.tila == "bus-off"


def test_sama_tunniste_on_virhe() -> None:
    with pytest.raises(ValueError):
        arbitraatio([Kehys(0x100, b"\x01"), Kehys(0x100, b"\x02")])

"""Suunnitelman ja täsmäytyksen ominaisuudet."""

from toimitus.tasmaytys import Tila, suunnittele, toteuta

HALUTTU: Tila = {"a": {"koko": 1}, "b": {"koko": 2}}


def test_tyhjasta_luodaan_kaikki() -> None:
    assert [m.laji for m in suunnittele(HALUTTU, {})] == ["luo", "luo"]


def test_toteutus_on_idempotentti() -> None:
    nykyinen: Tila = {"b": {"koko": 9}, "c": {"koko": 3}}
    ensimmainen = toteuta(HALUTTU, nykyinen)
    assert [(m.laji, m.nimi) for m in ensimmainen] == [
        ("luo", "a"), ("muuta", "b"), ("poista", "c")]
    assert nykyinen == HALUTTU
    assert toteuta(HALUTTU, nykyinen) == []


def test_toteutus_ei_jaa_tilaa_kuvauksen_kanssa() -> None:
    nykyinen: Tila = {}
    toteuta(HALUTTU, nykyinen)
    nykyinen["a"]["koko"] = 7            # ajautuma ei saa muuttaa kuvausta
    assert HALUTTU["a"]["koko"] == 1
    assert [m.selite for m in suunnittele(HALUTTU, nykyinen)] == [
        "koko: 7 -> 1"]

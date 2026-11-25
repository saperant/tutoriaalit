"""Putken ajurin omat testit: myös putki on koodia, joka voi olla rikki."""

from graphlib import CycleError
from pathlib import Path

import pytest

from toimitus.putki import Vaihe, aja


def onnistuu(_: Path) -> bool:
    return True


def epaonnistuu(_: Path) -> bool:
    return False


def test_vaiheet_ajetaan_riippuvuusjarjestyksessa(tmp_path: Path) -> None:
    ajetut: list[str] = []

    def kirjaa(nimi: str) -> Vaihe:
        def toiminto(_: Path) -> bool:
            ajetut.append(nimi)
            return True
        return Vaihe(nimi, toiminto, {"b": ("a",), "c": ("b",)}.get(nimi, ()))

    raportti = aja([kirjaa("c"), kirjaa("a"), kirjaa("b")], tmp_path)
    assert ajetut == ["a", "b", "c"]
    assert raportti.vihrea


def test_riippumattomat_vaiheet_samassa_aallossa(tmp_path: Path) -> None:
    raportti = aja([Vaihe("x", onnistuu), Vaihe("y", onnistuu),
                    Vaihe("z", onnistuu, ("x", "y"))], tmp_path)
    assert [[n for n, _ in aalto] for aalto in raportti.aallot] == [
        ["x", "y"], ["z"]]


def test_virheen_jalkeen_riippuvat_ohitetaan(tmp_path: Path) -> None:
    raportti = aja([Vaihe("testit", epaonnistuu),
                    Vaihe("tyyli", onnistuu),
                    Vaihe("paketti", onnistuu, ("testit", "tyyli")),
                    Vaihe("julkaisu", onnistuu, ("paketti",))], tmp_path)
    assert raportti.tilat == {"testit": "VIRHE", "tyyli": "ok",
                              "paketti": "ohitettu", "julkaisu": "ohitettu"}
    assert not raportti.vihrea
    assert raportti.ensimmainen_virhe == "testit"


def test_keha_ja_tuntematon_vaihe_hylataan(tmp_path: Path) -> None:
    with pytest.raises(CycleError):
        aja([Vaihe("a", onnistuu, ("b",)), Vaihe("b", onnistuu, ("a",))],
            tmp_path)
    with pytest.raises(ValueError, match="tuntematon vaihe"):
        aja([Vaihe("a", onnistuu, ("puuttuu",))], tmp_path)

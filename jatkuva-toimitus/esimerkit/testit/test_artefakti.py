"""Artefaktin toistettavuus ja käyttöönoton peruminen."""

import os
from pathlib import Path

from toimitus.artefakti import ota_kayttoon, peru, rakenna, tiiviste


def lahde(hak: Path, sisalto: str, aika: int) -> Path:
    (hak / "viite").mkdir(parents=True)
    tiedosto = hak / "viite" / "moduuli.py"
    tiedosto.write_text(sisalto, "utf-8")
    os.utime(tiedosto, (aika, aika))
    return hak


def test_sama_sisalto_antaa_saman_tiivisteen(tmp_path: Path) -> None:
    a = lahde(tmp_path / "a", "x = 1\n", 1_000_000)
    b = lahde(tmp_path / "b", "x = 1\n", 2_000_000)
    assert (tiiviste(rakenna(a, tmp_path / "ulos-a", "1.0"))
            == tiiviste(rakenna(b, tmp_path / "ulos-b", "1.0")))


def test_eri_sisalto_tai_versio_antaa_eri_tiivisteen(tmp_path: Path) -> None:
    a = lahde(tmp_path / "a", "x = 1\n", 1_000_000)
    b = lahde(tmp_path / "b", "x = 2\n", 1_000_000)
    perus = tiiviste(rakenna(a, tmp_path / "ulos-a", "1.0"))
    assert perus != tiiviste(rakenna(b, tmp_path / "ulos-b", "1.0"))
    assert perus != tiiviste(rakenna(a, tmp_path / "ulos-c", "1.1"))


def test_kayttoonotto_ja_peruminen(tmp_path: Path) -> None:
    a = lahde(tmp_path / "a", "x = 1\n", 1_000_000)
    ymparisto = tmp_path / "tuotanto"
    ota_kayttoon(rakenna(a, tmp_path / "varasto", "1.0"), ymparisto)
    ota_kayttoon(rakenna(a, tmp_path / "varasto", "1.1"), ymparisto)
    versio = ymparisto / "nykyinen" / "viite" / "VERSIO"
    assert versio.read_text("utf-8") == "1.1\n"
    peru(ymparisto)
    assert versio.read_text("utf-8") == "1.0\n"

"""Raporttityökalun testit: parametrisointi, fixturet, tmp_path,
monkeypatch ja tilannekuvatesti."""

import json
import os
from datetime import UTC, datetime
from pathlib import Path

import pytest

import raportti
from raportti import AjoTulos, Yhteenveto, lue, muotoile, yhteenveto

ODOTETUT = Path(__file__).with_name("odotetut")


# @alku fixture
def tulos(testi: str, tila: raportti.Tila, kesto: float = 1.0) -> AjoTulos:
    return {"testi": testi, "siemen": 1, "tila": tila, "kesto_s": kesto}


@pytest.fixture
def tulostiedosto(tmp_path: Path) -> Path:
    """Kolmen ajon tulostiedosto pytestin antamassa tilapäishakemistossa."""
    polku = tmp_path / "tulokset.jsonl"
    rivit = [tulos("uart", "läpi", 2.5), tulos("fifo", "aikaraja", 60.0),
             tulos("spi", "epäonnistui", 4.25)]
    polku.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n"
                             for r in rivit), encoding="utf-8")
    return polku


@pytest.fixture
def kiintea_aika(monkeypatch: pytest.MonkeyPatch) -> None:
    aika = datetime(2026, 11, 24, 8, 30, tzinfo=UTC)
    monkeypatch.setattr(raportti, "nyt", lambda: aika)
    monkeypatch.delenv("RAPORTTI_OTSIKKO", raising=False)
# @loppu fixture


# @alku parametrit
@pytest.mark.parametrize(("lapi", "ajoja", "odotettu"), [
    (0, 0, 0.0),        # tyhjä ajo ei saa jakaa nollalla
    (3, 3, 100.0),
    (2, 3, 66.67),
])
def test_lapaisyprosentti(lapi: int, ajoja: int, odotettu: float) -> None:
    y = Yhteenveto(ajoja, lapi, 0.0, ())
    assert y.lapaisyprosentti == pytest.approx(odotettu, abs=0.01)


def test_tuntematon_tila_hylataan(tmp_path: Path) -> None:
    polku = tmp_path / "huono.jsonl"
    polku.write_text('{"testi": "x", "siemen": 1, "tila": "ok", '
                     '"kesto_s": 1}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="huono.jsonl:1"):
        lue(polku)
# @loppu parametrit


# @alku tilannekuva
@pytest.mark.usefixtures("kiintea_aika")
def test_raportti(tulostiedosto: Path) -> None:
    teksti = muotoile(yhteenveto(lue(tulostiedosto)))
    odotettu = ODOTETUT / "raportti.txt"
    if os.environ.get("PAIVITA_ODOTETUT"):    # tarkoituksellinen muutos
        odotettu.write_text(teksti, encoding="utf-8")
    assert teksti == odotettu.read_text(encoding="utf-8")


@pytest.mark.usefixtures("kiintea_aika")
def test_otsikko_ymparistosta(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RAPORTTI_OTSIKKO", "Yöajo")
    assert muotoile(Yhteenveto(1, 1, 1.0, ())).startswith("Yöajo 2026")
# @loppu tilannekuva

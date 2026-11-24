"""Ajaa jokaisen esimerkin ja vertaa tulosteen .odotettu-tiedostoon.

Esimerkkimoduulissa on funktio ajo(ymp), joka tulostaa tuloksensa.
PAIVITA=1 kirjoittaa odotetut tulosteet uudelleen (tarkista erot gitillä).
"""

import importlib.util
import os
from pathlib import Path

import pytest

from nosql.kontit import Ymparisto

JUURI = Path(__file__).resolve().parent.parent
ESIMERKIT = sorted(p.with_suffix("") for p in JUURI.glob("luku*/*.odotettu"))


@pytest.mark.parametrize(
    "polku", ESIMERKIT, ids=[str(p.relative_to(JUURI)) for p in ESIMERKIT])
def test_esimerkki(polku: Path, ymp: Ymparisto,
                   capsys: pytest.CaptureFixture[str]) -> None:
    maaritys = importlib.util.spec_from_file_location(
        polku.name, polku.with_suffix(".py"))
    assert maaritys is not None and maaritys.loader is not None
    moduuli = importlib.util.module_from_spec(maaritys)
    maaritys.loader.exec_module(moduuli)
    moduuli.ajo(ymp)
    saatu = capsys.readouterr().out
    tiedosto = polku.with_suffix(".odotettu")
    if os.environ.get("PAIVITA"):
        tiedosto.write_text(saatu, "utf-8")
    assert saatu == tiedosto.read_text("utf-8")

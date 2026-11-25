"""Testi, joka joutuu kaivautumaan moduulin sisään."""

import random
from datetime import datetime, tzinfo
from typing import Self

import ennen
import pytest


# @alku paikkaus
class PerjantaiIlta(datetime):
    @classmethod
    def now(cls, tz: tzinfo | None = None) -> Self:
        return cls(2026, 11, 27, 16, 30)


def test_perjantai_illan_tilaus(monkeypatch: pytest.MonkeyPatch,
                                capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(ennen, "datetime", PerjantaiIlta)
    monkeypatch.setattr(random, "choice", lambda merkit: merkit[0])

    ennen.vahvista_tilaus(42)

    assert capsys.readouterr().out == (
        "Tilaus 42 lähtee 30.11. ja saapuu 02.12. Seurantakoodi: AAAAAA\n")
# @loppu paikkaus

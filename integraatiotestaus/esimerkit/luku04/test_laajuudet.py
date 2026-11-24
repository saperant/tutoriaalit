"""Fixturejen laajuudet ilman kontteja: pytest --setup-show näyttää,
milloin kukin fixture luodaan ja puretaan."""

from __future__ import annotations

from collections.abc import Iterator

import pytest


# @alku laajuudet
@pytest.fixture(scope="session")
def tietokanta() -> Iterator[str]:
    yield "kontti"          # käynnistetään kerran koko ajolle


@pytest.fixture(scope="module")
def skeema(tietokanta: str) -> Iterator[str]:
    yield "migroitu"        # kerran moduulia kohti


@pytest.fixture
def transaktio(skeema: str) -> Iterator[str]:
    yield "avoin"           # jokaiselle testille, perutaan lopuksi


def test_lisays(transaktio: str) -> None:
    assert transaktio == "avoin"


def test_haku(transaktio: str) -> None:
    assert transaktio == "avoin"
# @loppu laajuudet

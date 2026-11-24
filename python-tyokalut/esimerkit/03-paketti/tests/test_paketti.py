"""Paketin rakenteen testit: komentorivin sisääntulo, versio ja
toiminta. Ajetaan kehityshakemistosta (PYTHONPATH=src)."""

import importlib
import tomllib
from pathlib import Path

import pytest

import lokikoonti
from lokikoonti import cli

PROJEKTI = tomllib.loads(
    (Path(__file__).parents[1] / "pyproject.toml").read_text("utf-8"))


# @alku testit
def test_sisaantulot_ovat_olemassa() -> None:
    for nimi, kohde in PROJEKTI["project"]["scripts"].items():
        moduli, _, funktio = kohde.partition(":")
        assert callable(getattr(importlib.import_module(moduli), funktio)), \
            nimi


def test_versio_on_sama_kuin_pyprojectissa() -> None:
    assert lokikoonti.__version__ == PROJEKTI["project"]["version"]


def test_virheet_antavat_paluuarvon_1(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    loki = tmp_path / "sim.log"
    loki.write_text("@ 10 ns ERROR scb: ero\n@ 20 ns INFO tb: loppu\n",
                    encoding="utf-8")
    assert cli.main([str(loki)]) == 1
    assert "ERROR       1" in capsys.readouterr().out
# @loppu testit

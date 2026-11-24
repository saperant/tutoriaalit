"""Tallennuksen sopimustestit: sama sarja väärennökselle ja PostgreSQLille."""

from __future__ import annotations

import pytest

from varasto.malli import SaldoEiRiita, SkuVarattu, Tuote
from varasto.varasto import Varasto


# @alku sopimustestit
def test_haku_ei_valita_kirjainkoosta(varasto: Varasto) -> None:
    varasto.lisaa(Tuote("ABC-1", "Ruuvi", 10))
    assert varasto.hae("abc-1") == Tuote("ABC-1", "Ruuvi", 10)


def test_sama_sku_eri_kirjainkoolla_hylataan(varasto: Varasto) -> None:
    varasto.lisaa(Tuote("ABC-1", "Ruuvi", 10))
    with pytest.raises(SkuVarattu):
        varasto.lisaa(Tuote("abc-1", "Ruuvi (kopio)", 5))


def test_varaus_vahentaa_saldoa(varasto: Varasto) -> None:
    varasto.lisaa(Tuote("ABC-1", "Ruuvi", 10))
    varaus = varasto.varaa("abc-1", 3)
    assert (varaus.sku, varaus.maara) == ("ABC-1", 3)
    assert varaus.luotu.tzinfo is not None
    tuote = varasto.hae("ABC-1")
    assert tuote is not None and tuote.saldo == 7


def test_saldo_ei_mene_negatiiviseksi(varasto: Varasto) -> None:
    varasto.lisaa(Tuote("ABC-1", "Ruuvi", 2))
    with pytest.raises(SaldoEiRiita):
        varasto.varaa("ABC-1", 3)
    with pytest.raises(ValueError, match="positiivinen"):
        varasto.varaa("ABC-1", -1)
# @loppu sopimustestit


def test_varaukset_jarjestyksessa(varasto: Varasto) -> None:
    varasto.lisaa(Tuote("ABC-1", "Ruuvi", 10))
    ensimmainen = varasto.varaa("ABC-1", 1)
    toinen = varasto.varaa("abc-1", 2)
    assert [v.tunnus for v in varasto.varaukset("ABC-1")] == [
        ensimmainen.tunnus, toinen.tunnus]


def test_tuntematon_sku(varasto: Varasto) -> None:
    assert varasto.hae("EI-OLE") is None
    with pytest.raises(SaldoEiRiita):
        varasto.varaa("EI-OLE", 1)

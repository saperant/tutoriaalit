"""Yksikkötestit: palvelun logiikka väärennöksiä vasten, ei kontteja."""

from __future__ import annotations

import pytest

from varasto.hinnat import Hinta, HintaVirhe
from varasto.malli import SaldoEiRiita, Tuote
from varasto.palvelu import VarastoPalvelu
from varasto.varasto import MuistiVarasto


# @alku kaksoiset
class KiinteaHinta:
    """Tynkä (stub): palauttaa aina saman hinnan."""

    def hae(self, sku: str) -> Hinta:
        return Hinta(sku.upper(), 250, "EUR")


class KatkennutHinta:
    """Tynkä, joka simuloi hintapalvelun katkoa."""

    def hae(self, sku: str) -> Hinta:
        raise HintaVirhe("ei vastausta")


class Kirjuri:
    """Vakoilija (spy): kirjaa julkaistut tapahtumat tarkistettaviksi."""

    def __init__(self) -> None:
        self.tapahtumat: list[tuple[int, str, int]] = []

    def varattu(self, tunnus: int, sku: str, maara: int) -> None:
        self.tapahtumat.append((tunnus, sku, maara))
# @loppu kaksoiset


# @alku yksikkotesti
def test_tilaus_laskee_hinnan_ja_julkaisee_tapahtuman() -> None:
    varasto = MuistiVarasto()
    varasto.lisaa(Tuote("ABC-1", "Ruuvi", 10))
    kirjuri = Kirjuri()
    palvelu = VarastoPalvelu(varasto, KiinteaHinta(), kirjuri)

    tilaus = palvelu.tilaa("abc-1", 4)

    assert tilaus.yhteensa_snt == 1000
    assert kirjuri.tapahtumat == [(tilaus.varaus, "ABC-1", 4)]
    assert varasto.hae("ABC-1") == Tuote("ABC-1", "Ruuvi", 6)
# @loppu yksikkotesti


def test_hintakatko_ei_lukitse_saldoa() -> None:
    varasto = MuistiVarasto()
    varasto.lisaa(Tuote("ABC-1", "Ruuvi", 10))
    palvelu = VarastoPalvelu(varasto, KatkennutHinta(), Kirjuri())
    with pytest.raises(HintaVirhe):
        palvelu.tilaa("ABC-1", 4)
    assert varasto.hae("ABC-1") == Tuote("ABC-1", "Ruuvi", 10)


def test_liian_suuri_tilaus_ei_julkaise() -> None:
    varasto = MuistiVarasto()
    varasto.lisaa(Tuote("ABC-1", "Ruuvi", 2))
    kirjuri = Kirjuri()
    palvelu = VarastoPalvelu(varasto, KiinteaHinta(), kirjuri)
    with pytest.raises(SaldoEiRiita):
        palvelu.tilaa("ABC-1", 3)
    assert kirjuri.tapahtumat == []

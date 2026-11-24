"""Mock tarkistaa vuorovaikutuksen, ei käyttäytymistä."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import create_autospec

from varasto.hinnat import Hinta
from varasto.malli import Varaus
from varasto.palvelu import Hintalahde, Tapahtumat, VarastoPalvelu
from varasto.varasto import Varasto


# @alku mock
def test_tilaus_mockeilla() -> None:
    varasto = create_autospec(Varasto, instance=True)
    hinnat = create_autospec(Hintalahde, instance=True)
    tapahtumat = create_autospec(Tapahtumat, instance=True)
    # Paluuarvot ovat testin kirjoittajan oletuksia: oikea tietokanta
    # palauttaisi SKU:n tallennetussa muodossa 'ABC-1'.
    hinnat.hae.return_value = Hinta("abc-1", 250, "EUR")
    varasto.varaa.return_value = Varaus(
        7, "abc-1", 4, datetime(2026, 1, 1, tzinfo=UTC))

    tilaus = VarastoPalvelu(varasto, hinnat, tapahtumat).tilaa("abc-1", 4)

    assert tilaus.yhteensa_snt == 1000
    varasto.varaa.assert_called_once_with("abc-1", 4)
    tapahtumat.varattu.assert_called_once_with(7, "abc-1", 4)
# @loppu mock

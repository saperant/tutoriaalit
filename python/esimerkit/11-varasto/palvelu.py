"""Sovelluslogiikka: riippuu vain rajapinnasta, ei toteutuksesta."""

from dataclasses import replace
from typing import Protocol

from malli import Tuote, VarastoVirhe


class Tuotevarasto(Protocol):
    def hae(self, koodi: str) -> Tuote | None: ...
    def tallenna(self, tuote: Tuote) -> None: ...


class Varastopalvelu:
    def __init__(self, varasto: Tuotevarasto) -> None:
        self._varasto = varasto

    def ota(self, koodi: str, maara: int) -> Tuote:
        tuote = self._varasto.hae(koodi)
        if tuote is None:
            raise VarastoVirhe(f"tuntematon tuote {koodi}")
        if tuote.saldo < maara:
            raise VarastoVirhe(f"{tuote.nimi}: saldo {tuote.saldo} < {maara}")
        paivitetty = replace(tuote, saldo=tuote.saldo - maara)
        self._varasto.tallenna(paivitetty)
        return paivitetty

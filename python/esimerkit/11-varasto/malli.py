"""Toimialan tietotyypit: ei riippuvuuksia muihin moduuleihin."""

from dataclasses import dataclass

__all__ = ["Tuote", "VarastoVirhe"]


class VarastoVirhe(Exception):
    """Varastotoiminto ei onnistunut."""


@dataclass(frozen=True, slots=True)
class Tuote:
    koodi: str
    nimi: str
    saldo: int

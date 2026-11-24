"""Varaston tietomalli."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Tuote:
    """Varastonimike. SKU on yksilöivä tunnus kirjainkoosta riippumatta."""

    sku: str
    nimi: str
    saldo: int


@dataclass(frozen=True)
class Varaus:
    """Tilausta varten varattu määrä."""

    tunnus: int
    sku: str
    maara: int
    luotu: datetime


class VarastoVirhe(Exception):
    """Varaston sääntöä rikottiin (esim. saldo ei riitä)."""


class SkuVarattu(VarastoVirhe):
    """Samalla SKU:lla on jo tuote."""


class SaldoEiRiita(VarastoVirhe):
    """Varattava määrä ylittää saldon."""

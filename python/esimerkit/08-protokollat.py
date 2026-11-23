"""Rakenteellinen tyypitys protokollilla ja abstraktit kantaluokat."""

from abc import ABC, abstractmethod
from typing import Protocol


# @alku protokolla
class Tallennin(Protocol):
    """Mikä tahansa olio, jolla on nämä metodit, kelpaa."""

    def tallenna(self, avain: str, arvo: str) -> None: ...
    def hae(self, avain: str) -> str | None: ...


class Muistivarasto:                  # ei peri Tallenninta
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def tallenna(self, avain: str, arvo: str) -> None:
        self._data[avain] = arvo

    def hae(self, avain: str) -> str | None:
        return self._data.get(avain)


def muista_kayttaja(varasto: Tallennin, nimi: str) -> str:
    varasto.tallenna("kayttaja", nimi)
    return varasto.hae("kayttaja") or "?"


print(muista_kayttaja(Muistivarasto(), "Ada"))
# @loppu protokolla


# @alku abc
class Ilmoitus(ABC):
    """Kantaluokka, joka jakaa toteutusta: lähetys on yhteinen."""

    def laheta(self, viesti: str) -> str:
        return f"[{self.kanava()}] {self.muotoile(viesti)}"

    @abstractmethod
    def kanava(self) -> str: ...

    def muotoile(self, viesti: str) -> str:
        return viesti


class Tekstiviesti(Ilmoitus):
    def kanava(self) -> str:
        return "SMS"

    def muotoile(self, viesti: str) -> str:
        return viesti[:20]


print(Tekstiviesti().laheta("Tilauksesi on lähetetty tänään klo 14"))
try:
    Ilmoitus()  # type: ignore[abstract]
except TypeError:
    print("abstraktista luokasta ei voi luoda oliota")
# @loppu abc

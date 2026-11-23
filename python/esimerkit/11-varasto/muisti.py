"""Tuotevaraston toteutus muistissa (testeihin ja kokeiluihin)."""

from malli import Tuote


class Muistivarasto:
    def __init__(self, tuotteet: list[Tuote]) -> None:
        self._tuotteet = {t.koodi: t for t in tuotteet}

    def hae(self, koodi: str) -> Tuote | None:
        return self._tuotteet.get(koodi)

    def tallenna(self, tuote: Tuote) -> None:
        self._tuotteet[tuote.koodi] = tuote

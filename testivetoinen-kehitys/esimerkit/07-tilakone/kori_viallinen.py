"""Ostoskori, jossa poisto jättää tyhjän rivin koriin."""


class Kori:
    def __init__(self) -> None:
        self._maarat: dict[str, int] = {}

    def lisaa(self, tuote: str, maara: int) -> None:
        self._maarat[tuote] = self._maarat.get(tuote, 0) + maara

    # @alku vika
    def poista(self, tuote: str, maara: int) -> None:
        self._maarat[tuote] = max(0, self._maarat.get(tuote, 0) - maara)
    # @loppu vika

    def riveja(self) -> int:
        return len(self._maarat)

    def kappaleita(self) -> int:
        return sum(self._maarat.values())

"""Ostoskori, joka pitää kirjaa tuotteiden määristä."""


# @alku kori
class Kori:
    def __init__(self) -> None:
        self._maarat: dict[str, int] = {}

    def lisaa(self, tuote: str, maara: int) -> None:
        self._maarat[tuote] = self._maarat.get(tuote, 0) + maara

    def poista(self, tuote: str, maara: int) -> None:
        jaljella = self._maarat.get(tuote, 0) - maara
        if jaljella > 0:
            self._maarat[tuote] = jaljella
        else:
            self._maarat.pop(tuote, None)

    def riveja(self) -> int:
        return len(self._maarat)

    def kappaleita(self) -> int:
        return sum(self._maarat.values())
# @loppu kori

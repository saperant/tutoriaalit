"""Ostoskori, vaihe 4: summa lasketaan riveistä."""


# @alku kori
class Kori:
    def __init__(self) -> None:
        self._rivit: list[tuple[int, int]] = []

    def lisaa(self, tuote: str, hinta: int, maara: int) -> None:
        self._rivit.append((hinta, maara))

    def summa(self) -> int:
        return sum(hinta * maara for hinta, maara in self._rivit)
# @loppu kori

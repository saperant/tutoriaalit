"""Muistissa toimivat toteutukset: oikea logiikka ilman ulkomaailmaa."""


# @alku varasto
class MuistiVarasto:
    def __init__(self, saldot: dict[str, int]) -> None:
        self._saldot = dict(saldot)

    def saldo(self, tuote: str) -> int:
        return self._saldot[tuote]

    def varaa(self, tuote: str, maara: int) -> None:
        if self._saldot[tuote] < maara:
            raise ValueError(f"{tuote}: varastossa liian vähän")
        self._saldot[tuote] -= maara

    def vapauta(self, tuote: str, maara: int) -> None:
        self._saldot[tuote] += maara


class MuistiMaksut:
    """Hyväksyy veloitukset, paitsi suljetuilta korteilta."""

    def __init__(self, suljetut: set[str] | None = None) -> None:
        self._suljetut = suljetut or set()
        self.veloitettu = 0

    def veloita(self, kortti: str, sentit: int) -> bool:
        if kortti in self._suljetut:
            return False
        self.veloitettu += sentit
        return True
# @loppu varasto

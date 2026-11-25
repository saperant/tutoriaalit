"""Muistissa toimivat toteutukset: oikea logiikka ilman ulkomaailmaa."""


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

    # @alku kaikki
    def varaa_kaikki(self, ostokset: dict[str, int]) -> None:
        """Varaa kaiken tai ei mitään."""
        for tuote, maara in ostokset.items():
            if self._saldot[tuote] < maara:
                raise ValueError(f"{tuote}: varastossa liian vähän")
        for tuote, maara in ostokset.items():
            self._saldot[tuote] -= maara

    def vapauta_kaikki(self, ostokset: dict[str, int]) -> None:
        for tuote, maara in ostokset.items():
            self._saldot[tuote] += maara
    # @loppu kaikki


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

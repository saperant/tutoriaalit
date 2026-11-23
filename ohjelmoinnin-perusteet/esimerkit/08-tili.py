"""Pankkitili luokkana: data ja sitä koskevat säännöt yhdessä."""


class KateEiRiita(Exception):
    """Nostoa ei voi tehdä, koska saldo ei riitä."""


class Tili:
    """Pankkitili. Saldo on sentteinä eikä ole koskaan negatiivinen."""

    def __init__(self, omistaja: str, saldo: int = 0) -> None:
        if saldo < 0:
            raise ValueError("alkusaldo ei voi olla negatiivinen")
        self.omistaja = omistaja
        self._saldo = saldo        # alaviiva: älä muuta suoraan
        self._tapahtumat: list[int] = []

    @property
    def saldo(self) -> int:
        return self._saldo

    def talleta(self, summa: int) -> None:
        if summa <= 0:
            raise ValueError("talletuksen on oltava positiivinen")
        self._saldo += summa
        self._tapahtumat.append(summa)

    def nosta(self, summa: int) -> None:
        if summa <= 0:
            raise ValueError("noston on oltava positiivinen")
        if summa > self._saldo:
            raise KateEiRiita(f"saldo {self._saldo}, nosto {summa}")
        self._saldo -= summa
        self._tapahtumat.append(-summa)

    def __str__(self) -> str:
        return (f"{self.omistaja}: {self._saldo / 100:.2f} € "
                f"({len(self._tapahtumat)} tapahtumaa)")


aino = Tili("Aino", 5000)
eero = Tili("Eero")
aino.talleta(2500)
eero.talleta(1000)
try:
    eero.nosta(1500)
except KateEiRiita as virhe:
    print(f"Nosto hylättiin: {virhe}")
aino.nosta(1200)
print(aino)
print(eero)
print(aino.saldo, isinstance(aino, Tili))

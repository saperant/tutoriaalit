"""Tilauksen elinkaari ehtolauseilla: yksi tarkistus puuttuu."""

from tilaus import LaitonSiirtyma, Tila


# @alku viallinen
class Tilaus:
    def __init__(self, tila: Tila = Tila.UUSI) -> None:
        self.tila = tila

    def kasittele(self, tapahtuma: str) -> None:
        if tapahtuma == "maksa" and self.tila is Tila.UUSI:
            self.tila = Tila.MAKSETTU
        elif tapahtuma == "laheta" and self.tila is Tila.MAKSETTU:
            self.tila = Tila.LAHETETTY
        elif tapahtuma == "toimita" and self.tila is Tila.LAHETETTY:
            self.tila = Tila.TOIMITETTU
        elif tapahtuma == "peru" and self.tila is not Tila.TOIMITETTU:
            self.tila = Tila.PERUTTU      # vika: myös lähetetyn voi perua
        else:
            raise LaitonSiirtyma(f"{self.tila.value}: {tapahtuma}")
# @loppu viallinen

"""Tilauksen elinkaari tilakoneena: siirtymät ovat taulukossa."""

from enum import Enum


class Tila(Enum):
    UUSI = "uusi"
    MAKSETTU = "maksettu"
    LAHETETTY = "lähetetty"
    TOIMITETTU = "toimitettu"
    PERUTTU = "peruttu"


class LaitonSiirtyma(Exception):
    pass


# @alku siirtymat
SIIRTYMAT: dict[tuple[Tila, str], Tila] = {
    (Tila.UUSI, "maksa"): Tila.MAKSETTU,
    (Tila.UUSI, "peru"): Tila.PERUTTU,
    (Tila.MAKSETTU, "laheta"): Tila.LAHETETTY,
    (Tila.MAKSETTU, "peru"): Tila.PERUTTU,
    (Tila.LAHETETTY, "toimita"): Tila.TOIMITETTU,
}
TAPAHTUMAT = ("maksa", "laheta", "toimita", "peru")


class Tilaus:
    def __init__(self, tila: Tila = Tila.UUSI) -> None:
        self.tila = tila

    def kasittele(self, tapahtuma: str) -> None:
        avain = (self.tila, tapahtuma)
        if avain not in SIIRTYMAT:
            raise LaitonSiirtyma(f"{self.tila.value}: {tapahtuma}")
        self.tila = SIIRTYMAT[avain]
# @loppu siirtymat

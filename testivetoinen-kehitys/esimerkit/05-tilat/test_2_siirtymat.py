"""Siirtymätaulu kokonaan: myös ne siirtymät, joita ei saa tapahtua."""

from conftest import TilausLuokka
from tilaus import SIIRTYMAT, TAPAHTUMAT, LaitonSiirtyma, Tila


# @alku kaikki
def test_jokainen_tila_ja_tapahtuma(uusi_tilaus: TilausLuokka) -> None:
    poikkeamat = []
    for tila in Tila:
        for tapahtuma in TAPAHTUMAT:
            odotettu = SIIRTYMAT.get((tila, tapahtuma))
            tilaus = uusi_tilaus(tila)
            try:
                tilaus.kasittele(tapahtuma)
                saatu: Tila | None = tilaus.tila
            except LaitonSiirtyma:
                saatu = None
            if saatu is not odotettu:
                tulos = saatu.name if saatu else "virhe"
                poikkeamat.append(f"{tila.name} + {tapahtuma} -> {tulos}")

    assert not poikkeamat, poikkeamat
# @loppu kaikki

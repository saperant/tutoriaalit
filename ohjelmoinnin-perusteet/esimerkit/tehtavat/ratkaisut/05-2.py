"""Malliratkaisu 05-2: Yleisin sana."""


def yleisin(sanat: list[str]) -> str:
    """Palauttaa listan yleisimmän sanan."""
    lukumaarat: dict[str, int] = {}
    for sana in sanat:
        lukumaarat[sana] = lukumaarat.get(sana, 0) + 1
    suurin = max(lukumaarat.values())
    ehdokkaat = [sana for sana, maara in lukumaarat.items()
                 if maara == suurin]
    return min(ehdokkaat)

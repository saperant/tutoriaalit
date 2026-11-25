"""Malliratkaisu 07-2: Kelvollisten rivien summa."""


def summaa_kelvolliset(rivit: list[str]) -> tuple[int, list[int]]:
    """Palauttaa summan ja virheellisten rivien numerot."""
    summa = 0
    virheelliset = []
    for nro, rivi in enumerate(rivit, start=1):
        if not rivi.strip():
            continue
        try:
            summa += int(rivi)
        except ValueError:
            virheelliset.append(nro)
    return summa, virheelliset

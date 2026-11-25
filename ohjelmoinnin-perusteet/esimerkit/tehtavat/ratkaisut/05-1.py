"""Malliratkaisu 05-1: Parilliset luvut."""


def parilliset(luvut: list[int]) -> list[int]:
    """Palauttaa listan parilliset luvut."""
    return [luku for luku in luvut if luku % 2 == 0]

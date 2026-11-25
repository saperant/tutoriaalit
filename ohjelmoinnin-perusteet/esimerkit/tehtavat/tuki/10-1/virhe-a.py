"""Jokainen neljällä jaollinen vuosi on karkausvuosi (myös 1900)."""


def on_karkausvuosi(vuosi: int) -> bool:
    return vuosi % 4 == 0

"""Malliratkaisu 04-2: Karkausvuosi."""


def on_karkausvuosi(vuosi: int) -> bool:
    """Kertoo, onko vuosi karkausvuosi."""
    if vuosi % 400 == 0:
        return True
    if vuosi % 100 == 0:
        return False
    return vuosi % 4 == 0

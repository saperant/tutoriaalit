"""Karkausvuoden tunnistus (tehtävän 10-1 testattava moduli)."""


def on_karkausvuosi(vuosi: int) -> bool:
    """Kertoo, onko vuosi karkausvuosi gregoriaanisessa kalenterissa."""
    if vuosi % 400 == 0:
        return True
    if vuosi % 100 == 0:
        return False
    return vuosi % 4 == 0

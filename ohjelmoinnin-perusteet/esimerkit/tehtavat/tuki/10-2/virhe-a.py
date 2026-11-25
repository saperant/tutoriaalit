"""Tunniksi hyväksytään myös 24."""


def minuutteina(teksti: str) -> int:
    tunnit, erotin, minuutit = teksti.strip().partition(":")
    if not erotin or not tunnit.isdigit() or not minuutit.isdigit():
        raise ValueError(f"virheellinen kellonaika: '{teksti}'")
    if int(tunnit) > 24 or int(minuutit) > 59:
        raise ValueError(f"virheellinen kellonaika: '{teksti}'")
    return int(tunnit) * 60 + int(minuutit)

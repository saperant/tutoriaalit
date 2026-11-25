"""Minuuteiksi hyväksytään myös 60."""


def minuutteina(teksti: str) -> int:
    tunnit, erotin, minuutit = teksti.strip().partition(":")
    if not erotin or not tunnit.isdigit() or not minuutit.isdigit():
        raise ValueError(f"virheellinen kellonaika: '{teksti}'")
    if int(tunnit) > 23 or int(minuutit) > 60:
        raise ValueError(f"virheellinen kellonaika: '{teksti}'")
    return int(tunnit) * 60 + int(minuutit)

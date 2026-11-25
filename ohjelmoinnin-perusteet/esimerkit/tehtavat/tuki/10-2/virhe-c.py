"""Pelkkä luku ilman kaksoispistettä, kuten "7", kelpaa tunneiksi."""


def minuutteina(teksti: str) -> int:
    tunnit, _, minuutit = teksti.strip().partition(":")
    minuutit = minuutit or "0"
    if not tunnit.isdigit() or not minuutit.isdigit():
        raise ValueError(f"virheellinen kellonaika: '{teksti}'")
    if int(tunnit) > 23 or int(minuutit) > 59:
        raise ValueError(f"virheellinen kellonaika: '{teksti}'")
    return int(tunnit) * 60 + int(minuutit)

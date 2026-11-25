"""Keskiyö 0:00 hylätään virheellisenä."""


def minuutteina(teksti: str) -> int:
    tunnit, erotin, minuutit = teksti.strip().partition(":")
    if not erotin or not tunnit.isdigit() or not minuutit.isdigit():
        raise ValueError(f"virheellinen kellonaika: '{teksti}'")
    if int(tunnit) > 23 or int(minuutit) > 59:
        raise ValueError(f"virheellinen kellonaika: '{teksti}'")
    tulos = int(tunnit) * 60 + int(minuutit)
    if tulos == 0:
        raise ValueError(f"virheellinen kellonaika: '{teksti}'")
    return tulos

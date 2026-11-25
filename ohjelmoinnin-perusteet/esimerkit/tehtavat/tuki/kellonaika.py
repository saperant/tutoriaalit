"""Kellonajan jäsennys (tehtävän 10-2 testattava moduli)."""


def minuutteina(teksti: str) -> int:
    """Muuntaa kellonajan 't:mm' minuuteiksi keskiyöstä.

    Nostaa ValueErrorin, jos teksti ei ole kelvollinen kellonaika.
    """
    tunnit, erotin, minuutit = teksti.strip().partition(":")
    if not erotin or not tunnit.isdigit() or not minuutit.isdigit():
        raise ValueError(f"virheellinen kellonaika: '{teksti}'")
    if int(tunnit) > 23 or int(minuutit) > 59:
        raise ValueError(f"kellonaika ei ole vuorokaudessa: '{teksti}'")
    return int(tunnit) * 60 + int(minuutit)

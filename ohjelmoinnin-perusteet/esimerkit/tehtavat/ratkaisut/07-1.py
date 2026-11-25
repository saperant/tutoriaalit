"""Malliratkaisu 07-1: Iän jäsennys."""

SUURIN_IKA = 150


def jasenna_ika(teksti: str) -> int:
    """Palauttaa iän kokonaislukuna tai nostaa ValueErrorin."""
    try:
        ika = int(teksti.strip())
    except ValueError:
        raise ValueError(f"ikä ei ole kokonaisluku: '{teksti}'") from None
    if not 0 <= ika <= SUURIN_IKA:
        raise ValueError(f"ikä ei ole välillä 0–{SUURIN_IKA}: {ika}")
    return ika

"""Malliratkaisu 04-3: Postimaksu."""

PIKALISA_SNT = 300


def postimaksu(paino_g: int, pikana: bool = False) -> int:
    """Palauttaa lähetyksen hinnan sentteinä."""
    if paino_g <= 50:
        hinta = 250
    elif paino_g <= 250:
        hinta = 500
    elif paino_g <= 1000:
        hinta = 750
    else:
        hinta = 1200
    if pikana:
        hinta += PIKALISA_SNT
    return hinta

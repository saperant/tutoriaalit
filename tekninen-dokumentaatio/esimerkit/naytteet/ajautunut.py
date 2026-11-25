"""Esimerkki dokumentaatiosta, joka on jäänyt koodista jälkeen."""


def muunna(raaka_arvo: int, kerroin: float = 0.0625) -> float:
    """Muuntaa anturin raaka-arvon celsiusasteiksi.

    Args:
        raaka: AD-muuntimen lukema.

    Returns:
        Lämpötila celsiusasteina.
    """
    return raaka_arvo * kerroin


def kalibroi(lampotila: float) -> float:
    return lampotila - 0.4

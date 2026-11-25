"""Malliratkaisu 05-3: Yhteiset alkiot."""


def yhteiset(ensimmainen: list[str], toinen: list[str]) -> list[str]:
    """Palauttaa molemmissa listoissa esiintyvät merkkijonot."""
    return sorted(set(ensimmainen) & set(toinen))

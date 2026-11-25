"""Malliratkaisu 06-1: Nimikirjaimet."""


def nimikirjaimet(nimi: str) -> str:
    """Palauttaa nimen osien alkukirjaimet, esimerkiksi 'A. M. V.'."""
    return " ".join(f"{osa[0].upper()}." for osa in nimi.split())

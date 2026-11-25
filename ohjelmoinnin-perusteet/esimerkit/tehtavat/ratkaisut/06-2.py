"""Malliratkaisu 06-2: Palindromi."""


def on_palindromi(teksti: str) -> bool:
    """Kertoo, onko teksti palindromi."""
    merkit = [merkki for merkki in teksti.lower() if merkki.isalnum()]
    return merkit == merkit[::-1]

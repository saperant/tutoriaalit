"""Malliratkaisu 09-1: Viikonpäivä."""

from datetime import date

VIIKONPAIVAT = ["maanantai", "tiistai", "keskiviikko", "torstai",
                "perjantai", "lauantai", "sunnuntai"]


def viikonpaiva(paiva: str) -> str:
    """Palauttaa ISO-muotoisen päivämäärän viikonpäivän nimen."""
    return VIIKONPAIVAT[date.fromisoformat(paiva).weekday()]

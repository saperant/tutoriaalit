"""Malliratkaisu 09-2: Tilastot standardikirjastolla."""

import statistics


def tunnusluvut(luvut: list[float]) -> tuple[float, float]:
    """Palauttaa parin (keskiarvo, mediaani)."""
    return statistics.mean(luvut), statistics.median(luvut)

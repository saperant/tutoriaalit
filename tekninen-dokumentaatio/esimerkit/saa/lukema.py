"""Lukemarivien jäsentäminen ja tarkistus."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

#: Alin lämpötila, jonka anturi voi mitata (celsiusastetta).
ALIN_LAMPOTILA_C = -60.0
#: Ylin lämpötila, jonka anturi voi mitata (celsiusastetta).
YLIN_LAMPOTILA_C = 60.0


class LukemaVirhe(ValueError):
    """Lukemarivi on virheellinen.

    Viesti kertoo, mikä kenttä on vialla, jotta lähettäjä voi korjata
    rivin.
    """


# @alku lukema
@dataclass(frozen=True)
class Lukema:
    """Yksi aseman mittaus.

    Attributes:
        asema: Aseman tunnus, esimerkiksi ``"kumpula"``.
        aika: Mittaushetki. Aikavyöhyke on aina mukana.
        lampotila_c: Ilman lämpötila celsiusasteina.
        kosteus: Suhteellinen kosteus prosentteina tai ``None``, jos
            asemalla ei ole kosteusanturia.
    """

    asema: str
    aika: datetime
    lampotila_c: float
    kosteus: float | None = None
# @loppu lukema


# @alku jasenna
def jasenna_rivi(rivi: str) -> Lukema:
    """Jäsentää aseman lähettämän rivin lukemaksi.

    Rivin kentät erotetaan puolipisteellä: asema, aika ISO 8601
    -muodossa, lämpötila ja kosteus. Kosteus saa olla tyhjä.

    Args:
        rivi: Yksi rivi ilman rivinvaihtoa.

    Returns:
        Rivin sisältö tarkistettuna lukemana.

    Raises:
        LukemaVirhe: Jos kenttiä on väärä määrä, aika on ilman
            aikavyöhykettä tai arvo on anturin mittausalueen
            ulkopuolella.

    Example:
        >>> lukema = jasenna_rivi("kumpula;2026-11-25T12:00:00+02:00;-3.5;81")
        >>> lukema.lampotila_c
        -3.5
        >>> jasenna_rivi("kumpula;2026-11-25T12:00:00;-3.5;81")
        Traceback (most recent call last):
            ...
        saa.lukema.LukemaVirhe: aika: aikavyöhyke puuttuu
    """
    kentat = rivi.split(";")
    if len(kentat) != 4:
        raise LukemaVirhe(f"kenttiä on {len(kentat)}, pitää olla 4")
    asema, aika_teksti, lampo_teksti, kosteus_teksti = kentat
    if not asema:
        raise LukemaVirhe("asema: tunnus puuttuu")
    try:
        aika = datetime.fromisoformat(aika_teksti)
    except ValueError as virhe:
        raise LukemaVirhe(f"aika: {aika_teksti!r} ei ole ISO 8601") from virhe
    if aika.tzinfo is None:
        raise LukemaVirhe("aika: aikavyöhyke puuttuu")
    lampotila = _luku("lampotila_c", lampo_teksti)
    if not ALIN_LAMPOTILA_C <= lampotila <= YLIN_LAMPOTILA_C:
        raise LukemaVirhe(f"lampotila_c: {lampotila} on mittausalueen "
                          "ulkopuolella")
    kosteus = _luku("kosteus", kosteus_teksti) if kosteus_teksti else None
    if kosteus is not None and not 0.0 <= kosteus <= 100.0:
        raise LukemaVirhe(f"kosteus: {kosteus} ei ole välillä 0-100")
    return Lukema(asema, aika, lampotila, kosteus)
# @loppu jasenna


def _luku(kentta: str, teksti: str) -> float:
    try:
        return float(teksti)
    except ValueError as virhe:
        raise LukemaVirhe(f"{kentta}: {teksti!r} ei ole luku") from virhe

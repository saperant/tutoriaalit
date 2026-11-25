"""Alennusprosentti, josta yksi sääntöyhdistelmä on unohtunut."""


# @alku viallinen
def alennusprosentti(kanta_asiakas: bool, koodi: bool, iso: bool) -> int:
    if koodi:
        return 10
    if kanta_asiakas and iso:
        return 10
    if kanta_asiakas or iso:
        return 5
    return 0
# @loppu viallinen

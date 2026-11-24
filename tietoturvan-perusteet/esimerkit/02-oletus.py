"""Turvallinen oletus: virhetilanteessa pääsy evätään (fail closed)."""

KAYTTAJAT = {"aino": {"rooli": "admin"}, "pekka": {"rooli": "kayttaja"}}


# @alku avoin
def saa_poistaa_avoin(nimi: str) -> bool:
    """VIRHE: poikkeus tulkitaan luvaksi (fail open)."""
    try:
        return KAYTTAJAT[nimi]["rooli"] != "kayttaja"
    except KeyError:
        return True   # "ei tiedetä, päästetään läpi"
# @loppu avoin


# @alku suljettu
def saa_poistaa(nimi: str) -> bool:
    """Oikein: lupa vain, kun se on nimenomaisesti myönnetty."""
    kayttaja = KAYTTAJAT.get(nimi)
    if kayttaja is None:
        return False
    return kayttaja.get("rooli") == "admin"
# @loppu suljettu


for nimi in ["aino", "pekka", "tuntematon"]:
    print(f"{nimi:<11} avoin: {saa_poistaa_avoin(nimi)!s:<5} "
          f"suljettu: {saa_poistaa(nimi)}")

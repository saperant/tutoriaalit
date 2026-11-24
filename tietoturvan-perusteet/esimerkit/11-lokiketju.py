"""Rakenteinen turvallisuusloki, jonka muokkaus paljastuu (tiivisteketju)."""

import hashlib
import json

ALKU = "0" * 64


# @alku ketju
def lisaa(loki: list[str], tapahtuma: dict[str, str]) -> None:
    """Jokainen rivi sisältää edellisen rivin tiivisteen."""
    edellinen = (hashlib.sha256(loki[-1].encode()).hexdigest()
                 if loki else ALKU)
    loki.append(json.dumps({**tapahtuma, "edellinen": edellinen},
                           ensure_ascii=False, sort_keys=True))


def tarkista(loki: list[str]) -> int | None:
    """Ensimmäisen rikkoutuneen rivin numero tai None."""
    edellinen = ALKU
    for nro, rivi in enumerate(loki, 1):
        if json.loads(rivi)["edellinen"] != edellinen:
            return nro
        edellinen = hashlib.sha256(rivi.encode()).hexdigest()
    return None
# @loppu ketju


loki: list[str] = []
for tapahtuma in [
    {"aika": "09:00:45", "tyyppi": "kirjautuminen", "kayttaja": "aino",
     "tulos": "onnistui", "ip": "203.0.113.7"},
    {"aika": "09:02:10", "tyyppi": "oikeusmuutos", "kayttaja": "aino",
     "kohde": "aino", "uusi_rooli": "yllapito"},
    {"aika": "09:03:00", "tyyppi": "vienti", "kayttaja": "aino",
     "kohde": "asiakasrekisteri"},
]:
    lisaa(loki, tapahtuma)

print(loki[0][:72] + "…")
print("eheä:", tarkista(loki))
del loki[1]                          # hyökkääjä poistaa oikeusmuutoksen
print("rivi poistettu, ensimmäinen virhe rivillä:", tarkista(loki))

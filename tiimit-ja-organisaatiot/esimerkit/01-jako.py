"""Montako tiimiä yksi muutos vaatii kahdella eri tiimijaolla."""

from organisaatio import JAOT, KERROKSET, OMINAISUUDET

# @alku muutokset
# Tyypillisiä muutoksia ja osat, joihin ne koskevat.
MUUTOKSET = {
    "uusi suodatin hakuun": ["haku/ui", "haku/api", "haku/db"],
    "alennuskoodi koriin": ["kori/ui", "kori/api", "kori/db"],
    "painikkeen teksti": ["kori/ui"],
    "uusi maksutapa": ["maksu/ui", "maksu/api", "maksu/db", "tilaus/api"],
    "tilauksen peruutus": ["tilaus/ui", "tilaus/api", "tilaus/db",
                           "maksu/api"],
    "indeksi hakutauluun": ["haku/db"],
    "ulkoasun uudistus": [f"{o}/ui" for o in OMINAISUUDET],
    "tietokannan versiopäivitys": [f"{o}/db" for o in OMINAISUUDET],
}
# @loppu muutokset

assert KERROKSET == ["ui", "api", "db"]

# @alku laskenta
print(f"{'muutos':28}" + "".join(f"{nimi:>19}" for nimi in JAOT))
summat = dict.fromkeys(JAOT, 0)
for muutos, osat in MUUTOKSET.items():
    rivi = f"{muutos:28}"
    for nimi, jako in JAOT.items():
        tiimeja = len({jako(osa) for osa in osat})
        summat[nimi] += tiimeja
        rivi += f"{tiimeja:>19}"
    print(rivi)
print(f"{'yhteensä':28}" + "".join(f"{summat[n]:>19}" for n in JAOT))
# @loppu laskenta

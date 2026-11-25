"""Mitä pitää testata, kun vain osa repositoriosta muuttui?

Malli on sama kuin tämän tutoriaalikokoelman omassa CI:ssä: paketti
testataan, jos sen tiedostoja on muutettu, ja kaikki testataan, jos
muutos osuu yhteisiin tiedostoihin. Lisäksi tässä seurataan pakettien
välisiä riippuvuuksia.
"""

# @alku valinta
RIIPPUVUUDET = {             # paketti -> paketit, joita se käyttää
    "laskenta": [],
    "tietokanta": [],
    "rajapinta": ["laskenta", "tietokanta"],
    "raportit": ["laskenta"],
    "kayttoliittyma": ["rajapinta"],
}
YHTEISET = ("tyokalut/", "Makefile", ".github/")


def testattavat(muutetut: list[str]) -> list[str]:
    """Paketit, joihin muutos voi vaikuttaa, riippuvuuksia myöten."""
    if any(polku.startswith(YHTEISET) for polku in muutetut):
        return sorted(RIIPPUVUUDET)                 # varmuuden vuoksi kaikki
    valitut = {polku.split("/")[0] for polku in muutetut} & set(RIIPPUVUUDET)
    muuttui = True
    while muuttui:                                  # käyttäjät mukaan
        uudet = {paketti for paketti, kaytetyt in RIIPPUVUUDET.items()
                 if valitut & set(kaytetyt)} - valitut
        muuttui = bool(uudet)
        valitut |= uudet
    return sorted(valitut)
# @loppu valinta


TAPAUKSET = [
    ["raportit/kooste.py"],
    ["laskenta/alv.py"],
    ["tietokanta/skeema.sql", "LUEMINUT.md"],
    ["tyokalut/testaa.py"],
    ["LUEMINUT.md"],
]
for muutetut in TAPAUKSET:
    valitut = testattavat(muutetut)
    print(f"{', '.join(muutetut)}")
    print(f"  testataan {len(valitut)}/{len(RIIPPUVUUDET)}: "
          f"{', '.join(valitut) or '-'}")

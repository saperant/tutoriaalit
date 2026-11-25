"""Esimerkkiyrityksen verkkokauppa ja kaksi tapaa jakaa se tiimeille.

Muut esimerkit tuovat tämän moduulin. Järjestelmässä on neljä
ominaisuutta, ja jokaisessa on kolme kerrosta: käyttöliittymä (ui),
rajapinta (api) ja tietokanta (db).
"""

OMINAISUUDET = ["haku", "kori", "tilaus", "maksu"]
KERROKSET = ["ui", "api", "db"]
OSAT = [f"{o}/{k}" for o in OMINAISUUDET for k in KERROKSET]


# @alku riippuvuudet
def riippuvuudet() -> dict[str, list[str]]:
    """Mitä osia kukin osa kutsuu."""
    kutsut: dict[str, list[str]] = {}
    for o in OMINAISUUDET:
        kutsut[f"{o}/ui"] = [f"{o}/api"]
        kutsut[f"{o}/api"] = [f"{o}/db"]
        kutsut[f"{o}/db"] = []
    kutsut["kori/api"].append("haku/api")        # tuotetiedot
    kutsut["tilaus/api"].append("kori/api")      # korin sisältö
    kutsut["tilaus/api"].append("maksu/api")     # maksun aloitus
    kutsut["maksu/api"].append("tilaus/api")     # maksun tila tilaukselle
    return kutsut
# @loppu riippuvuudet


# @alku jaot
KERROSTIIMIT = {"ui": "käyttöliittymätiimi", "api": "rajapintatiimi",
                "db": "tietokantatiimi"}
VIRTATIIMIT = {"haku": "hakutiimi", "kori": "ostotiimi",
               "tilaus": "tilaustiimi", "maksu": "maksutiimi"}


def kerrosjako(osa: str) -> str:
    """Tiimi teknologiakerroksen mukaan: 3 tiimiä, 4 henkeä kussakin."""
    return KERROSTIIMIT[osa.split("/")[1]]


def virtajako(osa: str) -> str:
    """Tiimi ominaisuuden mukaan: 4 tiimiä, 3 henkeä kussakin."""
    return VIRTATIIMIT[osa.split("/")[0]]
# @loppu jaot


JAOT = {"kerroksittain": kerrosjako, "ominaisuuksittain": virtajako}

if __name__ == "__main__":
    kutsut = riippuvuudet()
    print(f"osia {len(OSAT)}, riippuvuuksia "
          f"{sum(len(k) for k in kutsut.values())}")
    for nimi, jako in JAOT.items():
        tiimit = sorted({jako(osa) for osa in OSAT})
        print(f"{nimi}: {len(tiimit)} tiimiä")

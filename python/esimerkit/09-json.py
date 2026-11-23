"""Ulkoisen datan tyypitys: TypedDict, Literal ja NewType."""

import json
from typing import Literal, NewType, TypedDict

# @alku tyypit
AsiakasId = NewType("AsiakasId", int)
Tila = Literal["avoin", "toimitettu", "peruttu"]


class Tilausrivi(TypedDict):
    tuote: str
    kpl: int


class Tilaus(TypedDict):
    asiakas: int
    tila: Tila
    rivit: list[Tilausrivi]
# @loppu tyypit


# @alku jasennys
def jasenna_tilaus(teksti: str) -> Tilaus:
    """json.loads palauttaa Any-tyypin: tarkistetaan ennen luottamista."""
    data = json.loads(teksti)
    if data.get("tila") not in ("avoin", "toimitettu", "peruttu"):
        raise ValueError(f"tuntematon tila: {data.get('tila')!r}")
    rivit: list[Tilausrivi] = [
        {"tuote": str(r["tuote"]), "kpl": int(r["kpl"])}
        for r in data["rivit"]
    ]
    return {"asiakas": int(data["asiakas"]), "tila": data["tila"],
            "rivit": rivit}


def laskuta(asiakas: AsiakasId, tilaus: Tilaus) -> str:
    kpl = sum(r["kpl"] for r in tilaus["rivit"])
    return f"asiakas {asiakas}: {kpl} kpl, tila {tilaus['tila']}"


tilaus = jasenna_tilaus('{"asiakas": 42, "tila": "avoin", '
                        '"rivit": [{"tuote": "kynä", "kpl": 3}]}')
print(laskuta(AsiakasId(tilaus["asiakas"]), tilaus))
try:
    jasenna_tilaus('{"asiakas": 1, "tila": "kadonnut", "rivit": []}')
except ValueError as virhe:
    print("hylätty:", virhe)
# @loppu jasennys

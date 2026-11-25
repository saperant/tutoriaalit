#!/usr/bin/env python3
"""Tarkistaa OpenAPI-kuvauksen toteutusta vasten.

Käyttö:  python3 openapi/tarkista.py KUVAUS.yaml

1. Kuvaus on kelvollista OpenAPI 3.1:tä.
2. Kuvauksen reitit ovat samat kuin toteutuksen (``saa.palvelu.REITIT``).
3. Jokainen esimerkkipyyntö ajetaan toteutuksella, ja vastauksen tila
   ja runko tarkistetaan kuvauksen skeemaa vasten.

Paluuarvo on 1, jos kuvaus ja toteutus eroavat.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from openapi_spec_validator import validate

from saa.palvelu import REITIT, Palvelu

LUKEMA = {"asema": "kumpula", "aika": "2026-11-25T12:00:00+02:00",
          "lampotila_c": -3.5, "kosteus": 81.0}


def avaa(solmu: Any, kuvaus: dict[str, Any]) -> Any:
    """Korvaa paikalliset $ref-viittaukset niiden kohteilla."""
    if isinstance(solmu, dict):
        if "$ref" in solmu:
            kohde: Any = kuvaus
            for osa in solmu["$ref"].removeprefix("#/").split("/"):
                kohde = kohde[osa]
            return avaa(kohde, kuvaus)
        return {k: avaa(v, kuvaus) for k, v in solmu.items()}
    if isinstance(solmu, list):
        return [avaa(x, kuvaus) for x in solmu]
    return solmu


# @alku kutsut
def kutsut(polku: str, metodi: str, toiminto: dict[str, Any]
           ) -> list[tuple[str, str, dict[str, Any] | None, dict[str, str]]]:
    """Muodostaa toiminnon esimerkeistä ajettavat pyynnöt."""
    kysely = {}
    for p in toiminto.get("parameters", []):
        if p["in"] == "path":
            polku = polku.replace("{" + p["name"] + "}", str(p["example"]))
        elif "example" in p:
            kysely[p["name"]] = str(p["example"])
    runko = toiminto.get("requestBody", {}).get("content", {}).get(
        "application/json", {})
    esimerkit = runko.get("examples", {})
    if not esimerkit:
        return [("esimerkki", polku, None, kysely)]
    return [(nimi, polku, e["value"], kysely)
            for nimi, e in esimerkit.items()]
# @loppu kutsut


# @alku tarkista
def tarkista(kuvaus: dict[str, Any]) -> list[str]:
    """Palauttaa kuvauksen ja toteutuksen erot."""
    erot = []
    kuvatut = {(m.upper(), polku) for polku, metodit
               in kuvaus["paths"].items() for m in metodit}
    for metodi, polku in sorted(kuvatut ^ set(REITIT)):
        missa = ("toteutuksesta" if (metodi, polku) in kuvatut
                 else "kuvauksesta")
        erot.append(f"{metodi} {polku}: puuttuu {missa}")
    for polku, metodit in kuvaus["paths"].items():
        for metodi, toiminto in metodit.items():
            for nimi, osoite, runko, kysely in kutsut(polku, metodi,
                                                     toiminto):
                palvelu = Palvelu()
                palvelu.kasittele("POST", "/lukemat", LUKEMA)   # pohjatila
                vastaus = palvelu.kasittele(metodi.upper(), osoite, runko,
                                            kysely)
                tunnus = f"{metodi.upper()} {polku} [{nimi}]"
                kuvattu = toiminto["responses"].get(str(vastaus.tila))
                if kuvattu is None:
                    erot.append(f"{tunnus}: tilaa {vastaus.tila} ei ole "
                                "kuvattu")
                    continue
                skeema = kuvattu["content"]["application/json"]["schema"]
                for virhe in Draft202012Validator(skeema).iter_errors(
                        vastaus.runko):
                    erot.append(f"{tunnus}: {vastaus.tila}: "
                                f"{virhe.message}")
                print(f"{tunnus}: {vastaus.tila}")
    return erot
# @loppu tarkista


def main() -> int:
    kuvaus = yaml.safe_load(Path(sys.argv[1]).read_text("utf-8"))
    validate(kuvaus)
    erot = tarkista(avaa(kuvaus, kuvaus))
    for ero in erot:
        print(f"ERO: {ero}")
    print("kuvaus ja toteutus "
          + ("eroavat" if erot else "vastaavat toisiaan"))
    return 1 if erot else 0


if __name__ == "__main__":
    sys.exit(main())

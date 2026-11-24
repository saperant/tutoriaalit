"""Kuluttajan sopimus tarkistetaan tuottajan kahta versiota vasten."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import jsonschema

from testiapu import kontit

SKEEMA_TIEDOSTO = Path(__file__).parent.parent / "sopimukset" / \
    "hinta-v1.schema.json"


# @alku tarkistus
def tarkista(rajapinta: str) -> None:
    skeema = json.loads(SKEEMA_TIEDOSTO.read_text("utf-8"))
    validoija = jsonschema.Draft202012Validator(skeema)
    with kontit.hintapalvelu(rajapinta=rajapinta) as palvelu:
        osoite = kontit.osoite(palvelu, 8080)
        with urllib.request.urlopen(f"{osoite}/hinnat/ABC-1",
                                    timeout=5) as vastaus:
            runko = json.loads(vastaus.read())
    print(f"tuottajan rajapinta {rajapinta}: {runko}")
    virheet = sorted(validoija.iter_errors(runko), key=str)
    for virhe in virheet:
        print("  sopimusrike:", virhe.message)
    if not virheet:
        print("  sopimus täyttyy")
# @loppu tarkistus


def main() -> None:
    kontit.apukuva().build()
    tarkista("1")
    tarkista("2")


if __name__ == "__main__":
    main()

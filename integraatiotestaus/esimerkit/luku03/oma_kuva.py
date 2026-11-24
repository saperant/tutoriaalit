"""Oma konttikuva testin sisällä: rakennetaan hintapalvelun väärennös
Dockerfilestä ja kysytään siltä hinta."""

from __future__ import annotations

import json
import urllib.request

from testiapu import kontit


# @alku oma_kuva
def main() -> None:
    kuva = kontit.apukuva().build()          # docker build apukuva/
    print("kuva:", kuva)
    with kontit.hintapalvelu() as palvelu:   # odottaa /terveys = 200
        osoite = kontit.osoite(palvelu, 8080)
        with urllib.request.urlopen(f"{osoite}/hinnat/xyz-9",
                                    timeout=5) as vastaus:
            print("tila:", vastaus.status)
            print("runko:", json.loads(vastaus.read()))
# @loppu oma_kuva


if __name__ == "__main__":
    main()

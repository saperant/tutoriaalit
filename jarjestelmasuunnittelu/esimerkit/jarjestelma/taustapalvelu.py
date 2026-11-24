"""Tilaton HTTP-taustapalvelu kuormantasaajan taakse.

    python3 -m jarjestelma.taustapalvelu --nimi a

GET /        vastaa {"palvelin": nimi, "pyynto": n}
GET /terveys vastaa 200, kun palvelu ottaa pyyntöjä vastaan

Palvelu kuuntelee käyttöjärjestelmän antamaa porttia ja tulostaa sen
ensimmäiselle riville muodossa "PORTTI 12345".
"""

from __future__ import annotations

import argparse
import itertools

from jarjestelma.http_apu import Kasittelija, kaynnista


def main() -> None:
    jasennin = argparse.ArgumentParser()
    jasennin.add_argument("--nimi", required=True)
    nimi = jasennin.parse_args().nimi
    laskuri = itertools.count(1)

    class Taustapalvelu(Kasittelija):
        def do_GET(self) -> None:  # noqa: N802 (http.serverin nimi)
            if self.path == "/terveys":
                self.vastaa(200, {"tila": "ok"})
            elif self.path == "/":
                self.vastaa(200, {"palvelin": nimi, "pyynto": next(laskuri)})
            else:
                self.vastaa(404, {"virhe": "ei löydy"})

    kaynnista(Taustapalvelu)


if __name__ == "__main__":
    main()

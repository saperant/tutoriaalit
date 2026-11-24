"""Hintapalvelun väärennös testejä varten (HTTP + JSON).

GET  /terveys               200, kun palvelu on valmis
GET  /hinnat/<sku>          {"sku", "hinta_snt", "valuutta"} tai 404
POST /hallinta/virheet?n=N  seuraavat N hintapyyntöä vastaavat 503

Ympäristömuuttuja RAJAPINTA=2 muuttaa vastauksen muotoa (kenttä
hinta_snt nimellä hinta euroina) sopimustestin esimerkkiä varten.
"""

from __future__ import annotations

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HINNAT = {"ABC-1": 1990, "XYZ-9": 450, "LMN-5": 12500}
VERSIO = os.environ.get("RAJAPINTA", "1")


class Tila:
    virheita_jaljella = 0
    lukko = threading.Lock()


# @alku kasittelija
class Kasittelija(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        polku = urlparse(self.path).path
        if polku == "/terveys":
            self._vastaa(200, {"tila": "ok"})
        elif polku.startswith("/hinnat/"):
            with Tila.lukko:
                if Tila.virheita_jaljella > 0:
                    Tila.virheita_jaljella -= 1
                    self._vastaa(503, {"virhe": "ylikuormitus"})
                    return
            sku = polku.removeprefix("/hinnat/").upper()
            if sku not in HINNAT:
                self._vastaa(404, {"virhe": "tuntematon sku"})
            elif VERSIO == "2":
                self._vastaa(200, {"sku": sku, "valuutta": "EUR",
                                   "hinta": HINNAT[sku] / 100})
            else:
                self._vastaa(200, {"sku": sku, "valuutta": "EUR",
                                   "hinta_snt": HINNAT[sku]})
        else:
            self._vastaa(404, {"virhe": "tuntematon polku"})
# @loppu kasittelija

    def do_POST(self) -> None:
        osat = urlparse(self.path)
        if osat.path == "/hallinta/virheet":
            n = int(parse_qs(osat.query).get("n", ["1"])[0])
            with Tila.lukko:
                Tila.virheita_jaljella = n
            self._vastaa(200, {"virheita": n})
        else:
            self._vastaa(404, {"virhe": "tuntematon polku"})

    def _vastaa(self, koodi: int, runko: dict[str, object]) -> None:
        data = json.dumps(runko).encode()
        self.send_response(koodi)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        """Pyyntölokia ei kirjoiteta: testien tuloste pysyy siistinä."""


if __name__ == "__main__":
    palvelin = ThreadingHTTPServer(("0.0.0.0", 8080), Kasittelija)
    print("hintapalvelu valmis", flush=True)
    palvelin.serve_forever()

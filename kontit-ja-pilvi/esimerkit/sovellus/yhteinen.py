"""Palvelujen yhteiset osat: JSON-vastaukset, lokitus ja sammutus.

Palvelut noudattavat twelve-factor-periaatteita: asetukset tulevat
ympäristömuuttujista, lokit kirjoitetaan rakenteisina riveinä
vakiotulosteeseen, ja SIGTERM sammuttaa palvelun hallitusti.
"""

from __future__ import annotations

import json
import os
import signal
import sys
import threading
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

Vastaus = tuple[int, dict[str, Any]]
Kasittelija = Callable[[str, str], Vastaus]


# @alku loki
def loki(taso: str, viesti: str, **kentat: Any) -> None:
    """Yksi JSON-rivi vakiotulosteeseen; ajoympäristö kerää lokit."""
    rivi = {"taso": taso, "viesti": viesti, **kentat}
    print(json.dumps(rivi, ensure_ascii=False), flush=True)
# @loppu loki


def asetus(nimi: str, oletus: str) -> str:
    return os.environ.get(nimi, oletus)


def palvelin(portti: int, kasittele: Kasittelija) -> ThreadingHTTPServer:
    """HTTP-palvelin, joka kutsuu funktiota kasittele(metodi, polku)."""

    class Pyynto(BaseHTTPRequestHandler):
        def _vastaa(self, metodi: str) -> None:
            tila, runko = kasittele(metodi, self.path)
            data = json.dumps(runko, ensure_ascii=False).encode()
            self.send_response(tila)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:
            self._vastaa("GET")

        def do_POST(self) -> None:
            self._vastaa("POST")

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            pass  # pyyntöloki tulisi tuotannossa rakenteisena

    return ThreadingHTTPServer(("0.0.0.0", portti), Pyynto)  # noqa: S104


# @alku sammutus
def aja(nimi: str, palvelin: ThreadingHTTPServer) -> None:
    """Palvelee, kunnes saadaan SIGTERM tai SIGINT, ja sammuu hallitusti.

    Kontin pysäytys lähettää ensin SIGTERMin ja vasta aikarajan jälkeen
    SIGKILLin. Käsittelyssä olevat pyynnöt saavat valmistua.
    """
    pysahdy = threading.Event()
    for s in (signal.SIGTERM, signal.SIGINT):
        signal.signal(s, lambda *_: pysahdy.set())
    saie = threading.Thread(target=palvelin.serve_forever)
    saie.start()
    loki("INFO", "käynnistetty", palvelu=nimi,
         portti=palvelin.server_address[1])
    pysahdy.wait()
    palvelin.shutdown()
    saie.join()
    palvelin.server_close()
    loki("INFO", "sammutettu", palvelu=nimi)
    sys.exit(0)
# @loppu sammutus

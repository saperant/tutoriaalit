"""Yhteiset palaset esimerkkien HTTP-palveluille (http.server).

http.server riittää esimerkeille. Tuotannossa palvelu ajettaisiin
kypsemmällä palvelimella (esim. asynkroninen kehys tai WSGI/ASGI-
palvelin), mutta samat asiat on hoidettava sielläkin:
- Naglen algoritmi pois, jotta pieni vastaus ei jää odottamaan
  vastapuolen viivästettyä kuittausta (noin 40 ms pysyvillä
  yhteyksillä),
- katkenneet yhteydet (terveystarkistus, asiakkaan aikaraja) eivät
  ole palvelun virheitä, eikä niistä kirjoiteta pinojälkeä.
"""

from __future__ import annotations

import json
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Palvelin(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request: object, client_address: object
                     ) -> None:
        pass   # katkenneet yhteydet: vastapuoli lähti, ei tehtävää


class Kasittelija(BaseHTTPRequestHandler):
    disable_nagle_algorithm = True

    def vastaa(self, koodi: int, sisalto: object,
               otsakkeet: dict[str, str] | None = None) -> None:
        """Vastaus yhdellä kirjoituksella: merkkijono tekstinä, muu
        JSON-muodossa."""
        if isinstance(sisalto, str):
            data, tyyppi = sisalto.encode(), "text/plain; charset=utf-8"
        else:
            data, tyyppi = json.dumps(sisalto).encode(), "application/json"
        self.send_response(koodi)
        self.send_header("Content-Type", tyyppi)
        self.send_header("Content-Length", str(len(data)))
        for nimi, arvo in (otsakkeet or {}).items():
            self.send_header(nimi, arvo)
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        pass   # ei pääsylokia; palvelut kirjaavat itse, mitä tarvitsevat


def kaynnista(kasittelija: type[Kasittelija], osoite: str = "127.0.0.1",
              portti: int = 0) -> None:
    """Käynnistää palvelun ja kertoo portin ensimmäisellä rivillä."""
    palvelin = Palvelin((osoite, portti), kasittelija)
    palvelin.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    print("PORTTI", palvelin.server_address[1], flush=True)
    palvelin.serve_forever()

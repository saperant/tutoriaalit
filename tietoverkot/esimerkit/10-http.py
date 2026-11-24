"""HTTP/1.1 sokeetin päällä: pyyntö, vastaus ja pysyvä yhteys."""

import http.server
import io
import json
import socket
import threading


class Kasittelija(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"       # pysyvät yhteydet käyttöön

    def do_GET(self) -> None:
        if self.path == "/saa":
            runko = json.dumps({"lampotila": -3.5}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "max-age=60")
        else:
            runko = b"ei loydy\n"
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(runko)))
        self.end_headers()
        self.wfile.write(runko)

    def log_message(self, format: str, *args: object) -> None:
        pass                              # ei lokia tulosteeseen


# @alku lue
Vastaus = tuple[str, dict[str, str], bytes]


def lue_vastaus(virta: io.BufferedIOBase) -> Vastaus:
    """Lukee yhden vastauksen: tilarivi, otsakkeet ja runko, jonka
    pituuden kertoo Content-Length."""
    tilarivi = virta.readline().decode().rstrip("\r\n")
    otsakkeet: dict[str, str] = {}
    while (rivi := virta.readline().decode().rstrip("\r\n")) != "":
        nimi, _, arvo = rivi.partition(":")
        otsakkeet[nimi.lower()] = arvo.strip()
    runko = virta.read(int(otsakkeet.get("content-length", "0")))
    return tilarivi, otsakkeet, runko or b""
# @loppu lue


def main() -> None:
    palvelin = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Kasittelija)
    threading.Thread(target=palvelin.serve_forever, daemon=True).start()
    portti = palvelin.server_address[1]

    # @alku pyynto
    with socket.create_connection(("127.0.0.1", portti)) as s:
        virta = s.makefile("rb")
        for polku in ["/saa", "/puuttuu"]:
            # Pyyntö on tekstiä: pyyntörivi, otsakkeet ja tyhjä rivi.
            pyynto = (f"GET {polku} HTTP/1.1\r\n"
                      "Host: saa.example\r\n"
                      "Accept: application/json\r\n"
                      "\r\n")
            s.sendall(pyynto.encode())
            tila, otsakkeet, runko = lue_vastaus(virta)
            print(tila)
            for nimi in ["content-type", "content-length", "cache-control"]:
                if nimi in otsakkeet:
                    print(f"  {nimi}: {otsakkeet[nimi]}")
            print(f"  runko: {runko.decode().strip()}")
    # Kaksi pyyntöä kulki samassa TCP-yhteydessä (HTTP/1.1 keep-alive).
    # @loppu pyynto
    palvelin.shutdown()


if __name__ == "__main__":
    main()

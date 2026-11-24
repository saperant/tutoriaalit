"""Lyhytosoitepalvelu: tilaton sovelluspalvelin.

    python3 -m jarjestelma.lyhyt --nimi a --pg 5432 --redis 6379 \\
        [--pg-isanta kanta] [--redis-isanta valimuisti]

POST /linkit   {"osoite": "https://..."} -> 201 {"koodi": "..."}
GET /<koodi>   302 Location: osoite, tai 404
GET /terveys   200, kun tietokanta vastaa
GET /metrics   Prometheuksen tekstimuoto

Tila on PostgreSQLissä ja välimuisti Redisissä, joten palvelimia voi
olla kuormantasaajan takana kuinka monta tahansa. Jos Redis ei vastaa,
palvelu toimii ilman välimuistia (siisti heikentyminen).
"""

from __future__ import annotations

import argparse
import json
import queue
import threading
from collections import Counter
from collections.abc import Iterator
from contextlib import contextmanager
from urllib.parse import urlsplit

import psycopg

from jarjestelma.http_apu import Kasittelija, kaynnista
from jarjestelma.resp import Redis, teksti
from jarjestelma.tunnus import koodi, numero

TTL = 3600            # s, löytynyt linkki
TTL_PUUTTUU = 60      # s, negatiivinen välimuisti: ei löydy


# @alku allas
class Allas:
    """Yhteysallas: yhteydet avataan kerran ja kierrätetään. Yhteyden
    avaus PostgreSQLiin maksaa prosessin käynnistyksen ja todennuksen,
    joten sitä ei tehdä pyyntöä kohden. Koko rajaa myös kannan
    rinnakkaiset kyselyt: pyyntö odottaa vapaata yhteyttä."""

    def __init__(self, isanta: str, portti: int, koko: int) -> None:
        self._vapaat: queue.Queue[psycopg.Connection[tuple[object, ...]]] \
            = queue.Queue()
        for _ in range(koko):   # salasana: PGPASSFILE tai PGPASSWORD
            self._vapaat.put(psycopg.connect(
                host=isanta, port=portti, user="tutoriaali",
                dbname="postgres", autocommit=True))

    @contextmanager
    def yhteys(self, odota_s: float = 2.0
               ) -> Iterator[psycopg.Connection[tuple[object, ...]]]:
        yhteys = self._vapaat.get(timeout=odota_s)  # queue.Empty: täynnä
        try:
            yield yhteys
        finally:
            self._vapaat.put(yhteys)
# @loppu allas


class Palvelu:
    def __init__(self, nimi: str, pg: tuple[str, int],
                 redis: tuple[str, int]) -> None:
        self.nimi = nimi
        self.allas = Allas(*pg, koko=4)
        self.redis = redis
        self._paikallinen = threading.local()
        self._lukko = threading.Lock()
        self.laskurit: Counter[str] = Counter()

    def laske(self, nimi: str) -> None:
        with self._lukko:
            self.laskurit[nimi] += 1

    def _redis(self) -> Redis:
        r = getattr(self._paikallinen, "redis", None)
        if r is None:
            r = Redis(self.redis[1], aikaraja=0.2, isanta=self.redis[0])
            self._paikallinen.redis = r
        return r

    def _hylkaa_redis(self) -> None:
        r = getattr(self._paikallinen, "redis", None)
        if r is not None:
            r.close()
        self._paikallinen.redis = None

    # @alku haku
    def hae(self, tunnus: str) -> tuple[str | None, str]:
        """Palauttaa osoitteen (None = ei ole) ja välimuistin tilan."""
        avain = f"linkki:{tunnus}"
        try:
            arvo = self._redis().komento("GET", avain)
            if arvo is not None:
                return (teksti(arvo) or None), "osuma"
            tila = "huti"
        except (OSError, ConnectionError):
            self._hylkaa_redis()
            tila = "ohitettu"                 # Redis alhaalla: kantaan
        self.laske("kantahaut")
        with self.allas.yhteys() as c:
            rivi = c.execute("SELECT osoite FROM linkit WHERE koodi = %s",
                             (tunnus,)).fetchone()
        osoite = str(rivi[0]) if rivi else None
        if tila == "huti":
            try:
                self._redis().komento("SET", avain, osoite or "", "EX",
                                      TTL if osoite else TTL_PUUTTUU)
            except (OSError, ConnectionError):
                self._hylkaa_redis()
        return osoite, tila
    # @loppu haku

    # @alku luonti
    def luo(self, osoite: str) -> str:
        osat = urlsplit(osoite)
        if osat.scheme not in ("http", "https") or not osat.netloc \
                or len(osoite) > 2048:
            raise ValueError("osoitteen on oltava http(s)-osoite")
        with self.allas.yhteys() as c:
            rivi = c.execute("SELECT nextval('linkki_numero')").fetchone()
            if rivi is None:
                raise RuntimeError("sekvenssi ei palauttanut arvoa")
            tunnus = koodi(int(str(rivi[0])))
            c.execute("INSERT INTO linkit (koodi, osoite) VALUES (%s, %s)",
                      (tunnus, osoite))
        return tunnus
    # @loppu luonti


def main() -> None:
    jasennin = argparse.ArgumentParser()
    jasennin.add_argument("--nimi", required=True)
    jasennin.add_argument("--pg", type=int, required=True)
    jasennin.add_argument("--pg-isanta", default="127.0.0.1")
    jasennin.add_argument("--redis", type=int, required=True)
    jasennin.add_argument("--redis-isanta", default="127.0.0.1")
    jasennin.add_argument("--osoite", default="127.0.0.1")
    jasennin.add_argument("--portti", type=int, default=0)
    a = jasennin.parse_args()
    palvelu = Palvelu(a.nimi, (a.pg_isanta, a.pg),
                      (a.redis_isanta, a.redis))

    class Lyhyt(Kasittelija):
        protocol_version = "HTTP/1.1"     # pysyvät yhteydet tasaajaan

        def do_POST(self) -> None:  # noqa: N802 (http.serverin nimi)
            if self.path != "/linkit":
                return self._lyhyt(404, {"virhe": "ei löydy"})
            try:
                pituus = int(self.headers.get("Content-Length", "0"))
                runko = json.loads(self.rfile.read(min(pituus, 4096)))
                tunnus = palvelu.luo(str(runko["osoite"]))
            except (ValueError, KeyError, TypeError) as virhe:
                return self._lyhyt(400, {"virhe": str(virhe)})
            self._lyhyt(201, {"koodi": tunnus})

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/terveys":
                with palvelu.allas.yhteys() as c:
                    c.execute("SELECT 1")
                return self._lyhyt(200, {"tila": "ok"})
            if self.path == "/metrics":
                rivit = [f'lyhyt_tapahtumat{{laji="{k}"}} {n}'
                         for k, n in sorted(palvelu.laskurit.items())]
                return self._lyhyt(200, "\n".join(rivit) + "\n")
            tunnus = self.path.lstrip("/")
            try:
                numero(tunnus)                 # torjuu roskan ennen hakua
            except ValueError:
                return self._lyhyt(404, {"virhe": "ei löydy"})
            osoite, tila = palvelu.hae(tunnus)
            palvelu.laske(f"valimuisti_{tila}")
            if osoite is None:
                return self._lyhyt(404, {"virhe": "ei löydy"}, tila)
            self._lyhyt(302, {}, tila, {"Location": osoite})

        def _lyhyt(self, koodi: int, sisalto: object, valimuisti: str = "",
                   otsakkeet: dict[str, str] | None = None) -> None:
            lisat = {"X-Palvelin": palvelu.nimi, **(otsakkeet or {})}
            if valimuisti:
                lisat["X-Valimuisti"] = valimuisti
            self.vastaa(koodi, sisalto, lisat)

    kaynnista(Lyhyt, a.osoite, a.portti)


if __name__ == "__main__":
    main()

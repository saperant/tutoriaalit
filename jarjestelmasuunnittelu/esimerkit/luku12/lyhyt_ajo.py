"""Lyhytosoitepalvelu kokonaisuutena: HAProxy, kaksi sovellus-
palvelinta, Redis ja PostgreSQL.

1. Luodaan 200 linkkiä kuormantasaajan kautta.
2. 3 000 uudelleenohjausta, suosio Zipfin mukaan, joukossa
   tuntemattomia koodeja.
3. Redis pysäytetään kesken kaiken: palvelu jatkaa ilman välimuistia.
Pyynnöt lähetetään peräkkäin, jotta välimuistin osumat ovat joka
ajolla samat.
"""

import email.message
import http.client
import itertools
import json
import random
from collections import Counter
from pathlib import Path

import psycopg

from jarjestelma import haproxy, tunnus
from jarjestelma.resp import Redis
from jarjestelma.ymparisto import Ymparisto, odota, vapaa_portti

TAMA = Path(__file__).parent


class Asiakas:
    """Yksi pysyvä HTTP-yhteys kuormantasaajaan; ei seuraa ohjauksia."""

    def __init__(self, portti: int) -> None:
        self._yhteys = http.client.HTTPConnection("127.0.0.1", portti,
                                                  timeout=5)

    def pyynto(self, metodi: str, polku: str, runko: object = None
               ) -> tuple[int, email.message.Message, bytes]:
        data = None if runko is None else json.dumps(runko).encode()
        self._yhteys.request(metodi, polku, body=data,
                             headers={"Content-Type": "application/json"})
        v = self._yhteys.getresponse()
        return v.status, v.headers, v.read()   # otsakkeet: kirjainkoko
                                               # ei ratkaise


def main() -> None:
    with Ymparisto() as ymp:
        # @alku kaynnistys
        pg = ymp.postgres()
        with psycopg.connect(host="127.0.0.1", port=pg.portti,
                             user="tutoriaali", dbname="postgres",
                             autocommit=True) as c:
            c.execute((TAMA / "skeema.sql").read_text())
        redis = ymp.redis("--maxmemory", "64mb",
                          "--maxmemory-policy", "allkeys-lru")
        api = [ymp.palvelu("jarjestelma.lyhyt", "--nimi", n,
                           "--pg", str(pg.portti), "--redis", str(redis))
               for n in "ab"]
        portti = vapaa_portti()
        hallinta = ymp.haproxy(TAMA / "haproxy.cfg", {
            "SISAAN": f"127.0.0.1:{portti}",
            "A_OSOITE": f"127.0.0.1:{api[0].portti}",
            "B_OSOITE": f"127.0.0.1:{api[1].portti}"})
        odota(lambda: set(haproxy.tilat(hallinta, "api").values())
              == {"UP"}, "sovelluspalvelimet UP")
        # @loppu kaynnistys
        asiakas = Asiakas(portti)

        # @alku kuorma
        koodit: list[str] = []
        palvelimet: Counter[str] = Counter()
        for i in range(200):
            tila, otsakkeet, runko = asiakas.pyynto(
                "POST", "/linkit", {"osoite": f"https://esimerkki.fi/s/{i}"})
            if tila != 201:
                raise RuntimeError(f"linkin luonti epäonnistui: {runko!r}")
            koodit.append(json.loads(runko)["koodi"])
            palvelimet[otsakkeet["X-Palvelin"]] += 1
        print(f"luotiin {len(set(koodit))} eri koodia, molemmat"
              f" palvelimet käytössä: {len(palvelimet) == 2}")
        tila, _, _ = asiakas.pyynto("POST", "/linkit", {"osoite": "ftp://x"})
        print("virheellinen osoite:", tila)

        s = random.Random(5)
        tuntematon = [tunnus.koodi(10 ** 9 + i) for i in range(20)]
        painot = list(itertools.accumulate(1 / i for i in range(1, 201)))
        tilastot: Counter[tuple[int, str]] = Counter()
        for _ in range(3000):
            koodi = s.choices(koodit, cum_weights=painot)[0] \
                if s.random() < 0.97 else tuntematon[s.randrange(20)]
            tila, otsakkeet, _ = asiakas.pyynto("GET", f"/{koodi}")
            tilastot[tila, otsakkeet.get("X-Valimuisti", "-")] += 1
        # @loppu kuorma
        for (tila, valimuisti), n in sorted(tilastot.items()):
            print(f"  {tila} {valimuisti:<6} {n}")

        # @alku heikentyminen
        with Redis(redis) as r:
            try:
                r.komento("SHUTDOWN", "NOSAVE")
            except ConnectionError:
                pass                       # Redis sulki yhteyden: odotettua
        ohjattu = Counter(
            asiakas.pyynto("GET", f"/{k}")[1].get("X-Valimuisti", "-")
            for k in koodit[:100])
        print("Redis pysäytetty, 100 uudelleenohjausta:", dict(ohjattu))
        # @loppu heikentyminen

        kantahaut = 0
        for palvelu in api:
            yhteys = http.client.HTTPConnection("127.0.0.1", palvelu.portti)
            yhteys.request("GET", "/metrics")
            for rivi in yhteys.getresponse().read().decode().splitlines():
                if rivi.startswith('lyhyt_tapahtumat{laji="kantahaut"}'):
                    kantahaut += int(rivi.split()[1])
        print(f"kantahakuja yhteensä {kantahaut} / 3100 lukua")


if __name__ == "__main__":
    main()

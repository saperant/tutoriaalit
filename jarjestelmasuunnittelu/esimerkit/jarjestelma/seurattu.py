"""Havaittava HTTP-palvelu: metriikat, rakenteiset lokit ja jäljitys.

    python3 -m jarjestelma.seurattu --nimi kauppa --alavirta 8001 \\
        --loki kauppa.jsonl

GET /tilaus/<n>  kauppa: kysyy varastolta /varasto/<n> ja vastaa
GET /varasto/<n> varasto: n % 10 == 7 on hidas, n % 10 == 9 epäonnistuu
GET /metrics     Prometheuksen tekstimuoto

Jäljitystieto kulkee W3C Trace Context -otsakkeessa
traceparent: 00-<jäljen tunnus>-<välin tunnus>-01. Jokainen palvelu
kirjaa pyynnöstä yhden JSON-rivin, jossa on jäljen ja välin tunnus
sekä vanhemman välin tunnus. Jäljen voi koota lokeista.
"""

from __future__ import annotations

import argparse
import json
import re
import secrets
import threading
import time
import urllib.error
import urllib.request
from collections import Counter

from jarjestelma.histogrammi import Histogrammi
from jarjestelma.http_apu import Kasittelija, kaynnista

RAJAT = [0.01, 0.05, 0.1, 0.25, 0.5, 1.0]
TRACEPARENT = re.compile(r"^00-([0-9a-f]{32})-([0-9a-f]{16})-0[01]$")


class Mittarit:
    def __init__(self, palvelu: str) -> None:
        self.palvelu = palvelu
        self._lukko = threading.Lock()
        self.pyynnot: Counter[tuple[str, int]] = Counter()
        self.kestot: dict[str, Histogrammi] = {}

    def kirjaa(self, reitti: str, koodi: int, kesto: float) -> None:
        with self._lukko:
            self.pyynnot[reitti, koodi] += 1
            self.kestot.setdefault(reitti, Histogrammi(RAJAT)) \
                .havainto(kesto)

    # @alku metrics
    def teksti(self) -> str:
        p = f'palvelu="{self.palvelu}"'
        rivit = ["# HELP http_pyynnot_yhteensa Käsitellyt pyynnöt.",
                 "# TYPE http_pyynnot_yhteensa counter"]
        with self._lukko:
            for (reitti, koodi), n in sorted(self.pyynnot.items()):
                rivit.append(f'http_pyynnot_yhteensa{{{p},reitti="{reitti}",'
                             f'koodi="{koodi}"}} {n}')
            rivit += ["# HELP http_kesto_sekunteina Pyynnön kesto.",
                      "# TYPE http_kesto_sekunteina histogram"]
            for reitti, h in sorted(self.kestot.items()):
                rivit += h.prometheus("http_kesto_sekunteina",
                                      f'{p},reitti="{reitti}"')
        return "\n".join(rivit) + "\n"
    # @loppu metrics


def main() -> None:
    jasennin = argparse.ArgumentParser()
    jasennin.add_argument("--nimi", required=True)
    jasennin.add_argument("--alavirta", type=int)
    jasennin.add_argument("--loki", required=True)
    asetukset = jasennin.parse_args()
    mittarit = Mittarit(asetukset.nimi)
    lokilukko = threading.Lock()

    class Seurattu(Kasittelija):
        def do_GET(self) -> None:  # noqa: N802 (http.serverin nimi)
            if self.path == "/metrics":
                self.vastaa(200, mittarit.teksti())
                return
            alku = time.monotonic()
            # @alku jalki
            osuma = TRACEPARENT.match(self.headers.get("traceparent", ""))
            jalki = osuma[1] if osuma else secrets.token_hex(16)
            vanhempi = osuma[2] if osuma else None
            vali = secrets.token_hex(8)
            # @loppu jalki
            reitti, _, tunnus = self.path.rpartition("/")
            koodi, teksti = self._kasittele(reitti, tunnus,
                                            f"00-{jalki}-{vali}-01")
            kesto = time.monotonic() - alku
            mittarit.kirjaa(reitti, koodi, kesto)
            rivi = {"palvelu": asetukset.nimi, "reitti": reitti,
                    "tunnus": tunnus, "koodi": koodi,
                    "kesto_ms": round(kesto * 1000, 1), "jalki": jalki,
                    "vali": vali, "vanhempi": vanhempi}
            with lokilukko, open(asetukset.loki, "a") as loki:
                loki.write(json.dumps(rivi) + "\n")
            self.vastaa(koodi, teksti)    # kirjattu ennen vastausta

        def _kasittele(self, reitti: str, tunnus: str,
                       traceparent: str) -> tuple[int, str]:
            if reitti == "/varasto" and tunnus.isdigit():
                n = int(tunnus)
                if n % 10 == 7:
                    time.sleep(0.5)            # hidas levyhaku
                if n % 10 == 9:
                    return 503, "varasto ei vastaa"
                return 200, f"tuote {n}: 3 kpl"
            if reitti == "/tilaus" and asetukset.alavirta:
                # @alku valitys
                pyynto = urllib.request.Request(
                    f"http://127.0.0.1:{asetukset.alavirta}/varasto/"
                    f"{tunnus}", headers={"traceparent": traceparent})
                try:
                    with urllib.request.urlopen(pyynto, timeout=2) as v:
                        return 200, v.read().decode()
                except (urllib.error.URLError, TimeoutError):
                    return 502, "varasto ei käytettävissä"
                # @loppu valitys
            return 404, "ei löydy"

    kaynnista(Seurattu)


if __name__ == "__main__":
    main()

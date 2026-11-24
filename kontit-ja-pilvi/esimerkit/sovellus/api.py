"""Käyntilaskurin rajapinta: kasvattaa laskuria ja kertoo käyntimäärän.

Ympäristömuuttujat:
  PORTTI       kuunneltava portti (oletus 8080)
  LASKURI_URL  laskuripalvelun osoite (oletus http://localhost:8081)
  VERSIO       palvelun versio, näkyy vastauksissa
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from yhteinen import Kasittelija, Vastaus, aja, asetus, loki, palvelin


def kutsu(osoite: str, metodi: str = "GET") -> dict[str, object]:
    if not osoite.startswith(("http://", "https://")):
        raise ValueError(f"vain HTTP-osoitteet: {osoite}")
    pyynto = urllib.request.Request(osoite, method=metodi)  # noqa: S310
    with urllib.request.urlopen(pyynto, timeout=2) as vastaus:  # noqa: S310
        tulos: dict[str, object] = json.load(vastaus)
        return tulos


# @alku kasittelija
def kasittelija(laskuri_url: str, versio: str) -> Kasittelija:
    def kasittele(metodi: str, polku: str) -> Vastaus:
        if polku == "/terveys":
            # Elävyys: prosessi vastaa. Ei riippuvuuksien tarkistusta,
            # jottei laskurin katko saa alustaa käynnistämään tätä
            # palvelua uudelleen turhaan.
            return 200, {"tila": "ok"}
        if polku == "/valmius":
            # Valmius: palvelu pystyy hoitamaan pyyntöjä.
            try:
                kutsu(f"{laskuri_url}/terveys")
            except (urllib.error.URLError, OSError):
                return 503, {"tila": "laskuri ei vastaa"}
            return 200, {"tila": "valmis"}
        if polku == "/" and metodi == "GET":
            try:
                tulos = kutsu(f"{laskuri_url}/laskuri", "POST")
            except (urllib.error.URLError, OSError) as virhe:
                loki("VIRHE", "laskuri ei vastaa", syy=str(virhe))
                return 503, {"virhe": "palvelu ei ole käytettävissä"}
            return 200, {"palvelu": "kaynnit", "versio": versio,
                         "kaynnit": tulos["arvo"]}
        return 404, {"virhe": "ei löydy"}
    return kasittele
# @loppu kasittelija


if __name__ == "__main__":
    kasittele = kasittelija(asetus("LASKURI_URL", "http://localhost:8081"),
                            asetus("VERSIO", "kehitys"))
    aja("api", palvelin(int(asetus("PORTTI", "8080")), kasittele))

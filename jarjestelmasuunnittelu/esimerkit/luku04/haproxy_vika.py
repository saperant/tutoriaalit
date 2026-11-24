"""Kuormantasaaja ja palvelimen kaatuminen kesken ajon.

Kolme tilatonta taustapalvelua HAProxyn takana. Palvelin b tapetaan
varoittamatta. Ennen kuin terveystarkistus huomaa kaatumisen, HAProxy
yrittää vielä lähettää b:lle, mutta yhteysvirheen jälkeen se yrittää
uudelleen toisella palvelimella (retries ja redispatch). Lopuksi
uusi b käynnistetään toiseen porttiin ja sen osoite vaihdetaan
ajonaikaisella rajapinnalla, kuten palveluhaku tekisi.
"""

import json
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

from jarjestelma import haproxy
from jarjestelma.ymparisto import Ymparisto, kaada, odota, vapaa_portti

ASETUS = Path(__file__).with_name("haproxy.cfg")


def pyynnot(portti: int, maara: int, jakauma_nakyviin: bool = True
            ) -> str:
    jakauma: Counter[str] = Counter()
    for _ in range(maara):
        try:
            with urllib.request.urlopen(
                    f"http://127.0.0.1:{portti}/", timeout=5) as vastaus:
                jakauma[json.load(vastaus)["palvelin"]] += 1
        except urllib.error.HTTPError as virhe:
            jakauma[f"HTTP {virhe.code}"] += 1
    if not jakauma_nakyviin:   # jakauma riippuu ajoituksesta
        onnistui = sum(n for k, n in jakauma.items() if len(k) == 1)
        return f"onnistui {onnistui}/{maara}"
    return " ".join(f"{k}={n}" for k, n in sorted(jakauma.items()))


def main() -> None:
    with Ymparisto() as ymp:
        palvelut = {n: ymp.palvelu("jarjestelma.taustapalvelu",
                                   "--nimi", n) for n in "abc"}
        portti = vapaa_portti()
        hallinta = ymp.haproxy(ASETUS, {
            "HAPROXY_PORTTI": str(portti),
            **{f"{n.upper()}_PORTTI": str(p.portti)
               for n, p in palvelut.items()}})
        kaikki_ylhaalla = lambda: set(  # noqa: E731
            haproxy.tilat(hallinta, "web").values()) == {"UP"}
        odota(kaikki_ylhaalla, "kaikki palvelimet UP")
        print("kaikki ylhäällä:  ", pyynnot(portti, 30))

        # @alku kaatuminen
        kaada(palvelut["b"])
        print("kaatumisen jälkeen:", pyynnot(portti, 9, False))
        odota(lambda: haproxy.tilat(hallinta, "web")["b"] == "DOWN",
              "b merkitty alas")
        print("b merkitty alas:  ", pyynnot(portti, 30))
        # @loppu kaatuminen

        # @alku palautus
        uusi = ymp.palvelu("jarjestelma.taustapalvelu", "--nimi", "b")
        vastaus = haproxy.komento(
            hallinta, f"set server web/b addr 127.0.0.1 port {uusi.portti}")
        print("hallinta: portti vaihdettu:", "port changed" in vastaus)
        odota(kaikki_ylhaalla, "uusi b UP")
        print("uusi b ylhäällä:  ", pyynnot(portti, 30))
        # @loppu palautus


if __name__ == "__main__":
    main()

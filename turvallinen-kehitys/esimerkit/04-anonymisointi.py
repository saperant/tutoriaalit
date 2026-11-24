"""Tuotantodatasta kehitysaineisto: pseudonymisointi, peitto ja yleistys.

Kehitysympäristöön ei kopioida henkilötietoja sellaisinaan. Tunnisteet
korvataan avaimellisella tiivisteellä (liitokset säilyvät), suorat
tunnisteet peitetään ja epäsuorat yleistetään. Lopuksi tarkistetaan,
ettei yksittäistä henkilöä voi poimia epäsuorien tietojen
yhdistelmästä.
"""

import hashlib
import hmac
from collections import Counter

Rivi = dict[str, str]

TUOTANTO: list[Rivi] = [
    {"asiakas": "1001", "nimi": "Aino Virtanen", "email": "aino@posti.fi",
     "syntynyt": "1988-03-14", "postinumero": "00530", "ostot": "12"},
    {"asiakas": "1002", "nimi": "Eero Laine", "email": "eero@posti.fi",
     "syntynyt": "1988-11-02", "postinumero": "00530", "ostot": "3"},
    {"asiakas": "1003", "nimi": "Liisa Koski", "email": "liisa@posti.fi",
     "syntynyt": "1991-06-30", "postinumero": "00530", "ostot": "7"},
    {"asiakas": "1004", "nimi": "Matti Niemi", "email": "matti@posti.fi",
     "syntynyt": "1988-01-21", "postinumero": "00530", "ostot": "1"},
    {"asiakas": "1005", "nimi": "Sanna Aho", "email": "sanna@posti.fi",
     "syntynyt": "1991-09-09", "postinumero": "00530", "ostot": "5"},
]


# @alku muunnos
def pseudonyymi(avain: bytes, arvo: str) -> str:
    """Sama syöte, sama pseudonyymi; ilman avainta ei käännettävissä."""
    return hmac.new(avain, arvo.encode(), hashlib.sha256).hexdigest()[:10]


def kehitykseen(rivi: Rivi, avain: bytes) -> Rivi:
    return {
        # liitokset toimivat pseudonyymin kautta
        "asiakas": pseudonyymi(avain, rivi["asiakas"]),
        "nimi": "Testi Henkilö",                     # suora tunniste pois
        "email": f"{pseudonyymi(avain, rivi['email'])}@example.invalid",
        "syntynyt": rivi["syntynyt"][:4],            # vain vuosi
        "postinumero": rivi["postinumero"][:3] + "00",   # alue, ei katu
        "ostot": rivi["ostot"],                      # hyötydata säilyy
    }
# @loppu muunnos


# @alku kanonymiteetti
def k_anonymiteetti(rivit: list[Rivi],
                    tunnisteet: tuple[str, ...]) -> int:
    """Pienin ryhmä, jossa epäsuorat tunnisteet ovat samat."""
    ryhmat = Counter(tuple(r[t] for t in tunnisteet) for r in rivit)
    return min(ryhmat.values())
# @loppu kanonymiteetti


def main() -> None:
    # Avain on vain muunnosajon salaisuus; se ei kulje aineiston mukana.
    avain = b"muunnosajon-kertakayttoavain"
    kehitys = [kehitykseen(r, avain) for r in TUOTANTO]
    for r in kehitys[:2]:
        print(r["asiakas"], r["email"], r["syntynyt"], r["postinumero"])
    epasuorat = ("syntynyt", "postinumero")
    print("k ennen yleistystä:", k_anonymiteetti(TUOTANTO, epasuorat))
    print("k yleistyksen jälkeen:", k_anonymiteetti(kehitys, epasuorat))
    uudelleen = kehitykseen(TUOTANTO[0], avain)
    sama = uudelleen["asiakas"] == kehitys[0]["asiakas"]
    print("pseudonyymi pysyy samana ajosta toiseen:", sama)


if __name__ == "__main__":
    main()

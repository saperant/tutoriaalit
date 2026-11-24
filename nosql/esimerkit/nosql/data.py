"""Esimerkkien yhteinen verkkokaupan data."""

from typing import Any

# @alku tuotteet
TUOTTEET: list[dict[str, Any]] = [
    {"_id": "keitin", "nimi": "Retkikeitin", "hinta": 49.0,
     "luokka": "retkeily", "ominaisuudet": {"paino_g": 380,
                                            "polttoaine": "kaasu"}},
    {"_id": "lamppu", "nimi": "Otsalamppu", "hinta": 29.0,
     "luokka": "valaisimet", "ominaisuudet": {"lumen": 400,
                                              "paristot": "AAA"}},
    {"_id": "pussi", "nimi": "Makuupussi", "hinta": 139.0,
     "luokka": "retkeily", "ominaisuudet": {"paino_g": 1200,
                                            "mukavuus_c": -5}},
    {"_id": "teltta", "nimi": "Kevytteltta", "hinta": 299.0,
     "luokka": "retkeily", "ominaisuudet": {"paino_g": 1900,
                                            "henkea": 2}},
]
# @loppu tuotteet

# @alku tilaukset
TILAUKSET: list[dict[str, Any]] = [
    {"_id": "T1", "asiakas": "aino", "kaupunki": "Oulu",
     "rivit": [{"tuote": "keitin", "kpl": 1, "hinta": 49.0},
               {"tuote": "lamppu", "kpl": 2, "hinta": 29.0}]},
    {"_id": "T2", "asiakas": "eero", "kaupunki": "Turku",
     "rivit": [{"tuote": "teltta", "kpl": 1, "hinta": 299.0}]},
    {"_id": "T3", "asiakas": "aino", "kaupunki": "Oulu",
     "rivit": [{"tuote": "pussi", "kpl": 1, "hinta": 139.0},
               {"tuote": "lamppu", "kpl": 1, "hinta": 29.0}]},
    {"_id": "T4", "asiakas": "ilona", "kaupunki": "Oulu",
     "rivit": [{"tuote": "keitin", "kpl": 2, "hinta": 45.0}]},
]
# @loppu tilaukset

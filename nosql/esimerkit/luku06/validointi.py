"""Skeemavalidointi: skeemattomuus on valinta, ei pakko."""

from typing import Any

from pymongo.errors import WriteError

from nosql.kontit import Ymparisto, aja

# @alku skeema
SKEEMA = {"$jsonSchema": {
    "bsonType": "object",
    "required": ["asiakas", "rivit"],
    "properties": {
        "asiakas": {"bsonType": "string", "minLength": 1},
        "rivit": {"bsonType": "array", "minItems": 1, "items": {
            "bsonType": "object", "required": ["tuote", "kpl"],
            "properties": {"kpl": {"bsonType": "int", "minimum": 1}}}},
    },
}}
# @loppu skeema


def ajo(ymp: Ymparisto) -> None:
    kanta = ymp.mongo()["kauppa06"]
    kanta.drop_collection("validoidut")
    # @alku kaytto
    kanta.create_collection("validoidut", validator=SKEEMA)
    tilaukset = kanta["validoidut"]
    yritykset: list[dict[str, Any]] = [
        {"asiakas": "aino", "rivit": [{"tuote": "keitin", "kpl": 1}]},
        {"asiakas": "eero", "rivit": []},
        {"asiakas": "ilona", "rivit": [{"tuote": "lamppu", "kpl": "2"}]},
        {"rivit": [{"tuote": "pussi", "kpl": 1}]},
    ]
    for i, dokumentti in enumerate(yritykset, start=1):
        try:
            tilaukset.insert_one(dokumentti)
            print(f"{i}: hyvaksytty")
        except WriteError as virhe:
            print(f"{i}: hylatty, koodi {virhe.code}")
    # @loppu kaytto


if __name__ == "__main__":
    aja(ajo)

"""Aggregaatioputki: myynti kaupungeittain ja tuotteittain."""

from typing import Any

from nosql.data import TILAUKSET
from nosql.kontit import Ymparisto, aja


def ajo(ymp: Ymparisto) -> None:
    kanta = ymp.mongo()["kauppa06"]
    kanta.drop_collection("tilaukset")
    kanta["tilaukset"].insert_many(TILAUKSET)

    # @alku putki
    putki: list[dict[str, Any]] = [
        {"$unwind": "$rivit"},
        {"$group": {
            "_id": {"kaupunki": "$kaupunki", "tuote": "$rivit.tuote"},
            "kpl": {"$sum": "$rivit.kpl"},
            "euroa": {"$sum": {"$multiply": ["$rivit.kpl",
                                             "$rivit.hinta"]}}}},
        {"$sort": {"euroa": -1, "_id.tuote": 1}},
        {"$limit": 4},
        {"$project": {"_id": 0, "kaupunki": "$_id.kaupunki",
                      "tuote": "$_id.tuote", "kpl": 1, "euroa": 1}},
    ]
    for rivi in kanta["tilaukset"].aggregate(putki):
        print(rivi)
    # @loppu putki

    # @alku asiakkaat
    asiakkaat = kanta["tilaukset"].aggregate([
        {"$group": {"_id": "$asiakas", "tilauksia": {"$count": {}}}},
        {"$match": {"tilauksia": {"$gte": 2}}},
    ])
    print("kanta-asiakkaat:", [a["_id"] for a in asiakkaat])
    # @loppu asiakkaat


if __name__ == "__main__":
    aja(ajo)

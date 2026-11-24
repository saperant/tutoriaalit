"""Upotus vai viittaus: tilauksen rivit ja tuotetiedot."""

from typing import Any

from nosql.data import TILAUKSET, TUOTTEET
from nosql.kontit import Ymparisto, aja


def ajo(ymp: Ymparisto) -> None:
    kanta = ymp.mongo()["kauppa05"]
    for nimi in ("tuotteet", "tilaukset"):
        kanta.drop_collection(nimi)
    kanta["tuotteet"].insert_many(TUOTTEET)
    kanta["tilaukset"].insert_many(TILAUKSET)

    # @alku upotettu
    tilaus = kanta["tilaukset"].find_one({"_id": "T1"}) or {}
    summa = sum(r["kpl"] * r["hinta"] for r in tilaus["rivit"])
    print("T1 yhdella haulla, summa:", summa)
    # @loppu upotettu

    # @alku lookup
    putki: list[dict[str, Any]] = [
        {"$match": {"_id": "T1"}},
        {"$unwind": "$rivit"},
        {"$lookup": {"from": "tuotteet", "localField": "rivit.tuote",
                     "foreignField": "_id", "as": "tuote"}},
        {"$project": {"_id": 0, "tuote": {"$first": "$tuote.nimi"},
                      "kpl": "$rivit.kpl"}},
    ]
    for rivi in kanta["tilaukset"].aggregate(putki):
        print("T1:", rivi)
    # @loppu lookup

    # @alku kasvu
    koko = kanta.command("collStats", "tilaukset")["avgObjSize"]
    print("tilausdokumentin koko alle 1 kt:", koko < 1024)
    # @loppu kasvu


if __name__ == "__main__":
    aja(ajo)

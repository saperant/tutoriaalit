"""Dokumenttien lisääminen, haku ja päivitys MongoDB:ssä."""

from nosql.data import TUOTTEET
from nosql.kontit import Ymparisto, aja


def ajo(ymp: Ymparisto) -> None:
    kanta = ymp.mongo()["kauppa05"]
    kanta.drop_collection("tuotteet")
    tuotteet = kanta["tuotteet"]

    # @alku lisays
    tuotteet.insert_many(TUOTTEET)
    print("tuotteita:", tuotteet.count_documents({}))
    # @loppu lisays

    # @alku haku
    halvat = tuotteet.find(
        {"luokka": "retkeily", "hinta": {"$lt": 200}},
        {"nimi": 1, "hinta": 1, "_id": 0}).sort("hinta", 1)
    for t in halvat:
        print("retkeily < 200:", t)
    kevyet = tuotteet.find({"ominaisuudet.paino_g": {"$lte": 1200}},
                           {"_id": 1}).sort("_id", 1)
    print("paino <= 1200 g:", [t["_id"] for t in kevyet])
    # @loppu haku

    # @alku paivitys
    tuotteet.update_one({"_id": "lamppu"},
                        {"$set": {"hinta": 24.0},
                         "$push": {"arviot": {"tahtia": 5}}})
    tuotteet.update_many({"luokka": "retkeily"},
                         {"$inc": {"hinta": 10}})
    tulos = tuotteet.update_one({"_id": "kompassi"},
                                {"$setOnInsert": {"nimi": "Kompassi",
                                                  "hinta": 19.0}},
                                upsert=True)
    print("upsert loi uuden:", tulos.upserted_id)
    lamppu = tuotteet.find_one({"_id": "lamppu"}, {"_id": 0, "nimi": 1,
                                                    "hinta": 1, "arviot": 1})
    print("lamppu:", lamppu)
    # @loppu paivitys


if __name__ == "__main__":
    aja(ajo)

"""Monen dokumentin transaktio: varaus ja tilaus yhdessä."""

import functools

from pymongo.client_session import ClientSession

from nosql.kontit import Ymparisto, aja


class EiRiita(Exception):
    pass


def ajo(ymp: Ymparisto) -> None:
    asiakas = ymp.mongo()
    kanta = asiakas["kauppa06"]
    for nimi in ("varasto", "tilaukset_tx"):
        kanta.drop_collection(nimi)
    kanta["varasto"].insert_one({"_id": "teltta", "saldo": 1})
    kanta.create_collection("tilaukset_tx")

    # @alku transaktio
    def tilaa(istunto: ClientSession, tilaus: str) -> None:
        tulos = kanta["varasto"].update_one(
            {"_id": "teltta", "saldo": {"$gte": 1}},
            {"$inc": {"saldo": -1}}, session=istunto)
        kanta["tilaukset_tx"].insert_one(
            {"_id": tilaus, "tuote": "teltta"}, session=istunto)
        if tulos.modified_count == 0:
            raise EiRiita(tilaus)      # perutaan myös tilauksen lisäys

    for tilaus in ["T10", "T11"]:
        with asiakas.start_session() as istunto:
            try:
                istunto.with_transaction(
                    functools.partial(tilaa, tilaus=tilaus))
                print(tilaus, "vahvistettu")
            except EiRiita:
                print(tilaus, "peruttu: varasto loppui")
    print("tilauksia:", kanta["tilaukset_tx"].count_documents({}),
          "saldo:", kanta["varasto"].find_one({"_id": "teltta"},
                                              {"_id": 0}))
    # @loppu transaktio


if __name__ == "__main__":
    aja(ajo)

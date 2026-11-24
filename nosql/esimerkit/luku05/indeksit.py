"""Indeksit ja kyselysuunnitelma (explain)."""

from typing import Any

from pymongo import ASCENDING, DESCENDING

from nosql.kontit import Ymparisto, aja


def vaiheet(suunnitelma: dict[str, Any]) -> list[str]:
    """Voittaneen suunnitelman vaiheet sisimmästä uloimpaan."""
    tulos: list[str] = []
    vaihe: dict[str, Any] | None = suunnitelma
    while vaihe:
        tulos.append(vaihe["stage"])
        vaihe = vaihe.get("inputStage")
    return list(reversed(tulos))


def ajo(ymp: Ymparisto) -> None:
    kanta = ymp.mongo()["kauppa05"]
    kanta.drop_collection("tilaukset_iso")
    tilaukset = kanta["tilaukset_iso"]
    kaupungit = ["Oulu", "Turku", "Tampere", "Espoo", "Kuopio"]
    tilaukset.insert_many(
        {"_id": i, "kaupunki": kaupungit[i % 5], "summa": (i * 37) % 500,
         "paiva": 1 + i % 30} for i in range(10_000))

    # @alku explain
    def selita(kysely: dict[str, Any], jarjestys: str | None = None) -> None:
        kursori = tilaukset.find(kysely)
        if jarjestys:
            kursori = kursori.sort(jarjestys, DESCENDING)
        tieto = kursori.explain()
        voittaja = tieto["queryPlanner"]["winningPlan"]
        tilasto = tieto["executionStats"]
        print(" -> ".join(vaiheet(voittaja.get("queryPlan", voittaja))),
              "| luettu", tilasto["totalDocsExamined"],
              "| palautettu", tilasto["nReturned"])

    kysely = {"kaupunki": "Oulu", "summa": {"$gte": 450}}
    selita(kysely)
    tilaukset.create_index([("kaupunki", ASCENDING), ("summa", ASCENDING)])
    selita(kysely)
    # @loppu explain

    # @alku esr
    selita({"kaupunki": "Oulu", "paiva": {"$lte": 3}}, "summa")
    tilaukset.create_index([("kaupunki", ASCENDING), ("summa", ASCENDING),
                            ("paiva", ASCENDING)])
    selita({"kaupunki": "Oulu", "paiva": {"$lte": 3}}, "summa")
    # @loppu esr


if __name__ == "__main__":
    aja(ajo)

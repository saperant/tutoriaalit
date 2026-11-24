"""MongoDB:n kirjoitus- ja lukutakuut (write/read concern)."""

from pymongo import WriteConcern
from pymongo.errors import WriteConcernError, WriteError
from pymongo.read_concern import ReadConcern

from nosql.kontit import Ymparisto, aja


def ajo(ymp: Ymparisto) -> None:
    kanta = ymp.mongo()["luku10"]
    kanta.drop_collection("tilaukset")
    tilaukset = kanta["tilaukset"]

    # @alku kuittaus
    tasot: list[int | str] = [1, "majority"]
    for w in tasot:
        kokoelma = tilaukset.with_options(
            write_concern=WriteConcern(w=w, wtimeout=2000))
        tulos = kokoelma.insert_one({"tilaus": f"T-{w}"})
        print(f"w={w}: kuitattu={tulos.acknowledged}")
    # @loppu kuittaus

    # @alku liikaa
    kaksi = tilaukset.with_options(write_concern=WriteConcern(w=2,
                                                              wtimeout=2000))
    try:
        kaksi.insert_one({"tilaus": "T-2"})
    except (WriteConcernError, WriteError) as virhe:
        print("w=2 yhden solmun joukossa:", type(virhe).__name__)
    print("tallessa silti:", tilaukset.count_documents({"tilaus": "T-2"}))
    # @loppu liikaa

    # @alku luku
    enemmisto = tilaukset.with_options(read_concern=ReadConcern("majority"))
    print("majority-kirjoitus nakyy majority-luvulle:",
          enemmisto.count_documents({"tilaus": "T-majority"}))
    # @loppu luku


if __name__ == "__main__":
    aja(ajo)

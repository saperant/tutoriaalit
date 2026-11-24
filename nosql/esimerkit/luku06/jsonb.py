"""Sama tehtävä PostgreSQLin JSONB-sarakkeella."""

import json

from nosql.data import TILAUKSET
from nosql.kontit import Ymparisto, aja


def ajo(ymp: Ymparisto) -> None:
    kanta = ymp.postgres()
    # @alku taulu
    kanta.execute("DROP TABLE IF EXISTS tilaukset")
    kanta.execute("""
        CREATE TABLE tilaukset (
            id    text PRIMARY KEY,
            data  jsonb NOT NULL
                  CHECK (jsonb_typeof(data -> 'rivit') = 'array')
        )""")
    with kanta.cursor() as kursori:
        kursori.executemany(
            "INSERT INTO tilaukset VALUES (%s, %s)",
            [(t["_id"], json.dumps({k: v for k, v in t.items()
                                    if k != "_id"})) for t in TILAUKSET])
    kanta.execute("CREATE INDEX ON tilaukset USING gin (data)")
    # @loppu taulu

    # @alku kysely
    rivit = kanta.execute("""
        SELECT t.data ->> 'kaupunki' AS kaupunki,
               r ->> 'tuote'         AS tuote,
               sum((r ->> 'kpl')::int)                       AS kpl,
               sum((r ->> 'kpl')::int * (r ->> 'hinta')::numeric) AS euroa
        FROM tilaukset t, jsonb_array_elements(t.data -> 'rivit') r
        GROUP BY 1, 2
        ORDER BY euroa DESC, tuote
        LIMIT 4""").fetchall()
    for kaupunki, tuote, kpl, euroa in rivit:
        print(kaupunki, tuote, kpl, f"{euroa:.1f}")
    # @loppu kysely

    # @alku sisaltaa
    oulu = kanta.execute(
        "SELECT id FROM tilaukset WHERE data @> %s ORDER BY id",
        (json.dumps({"kaupunki": "Oulu"}),)).fetchall()
    print("Oulun tilaukset:", [r[0] for r in oulu])
    # @loppu sisaltaa


if __name__ == "__main__":
    aja(ajo)

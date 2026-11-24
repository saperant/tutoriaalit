"""Sama tilaus normalisoituna ja dokumenttina (PostgreSQL)."""

import json

from nosql.data import TILAUKSET, TUOTTEET
from nosql.kontit import Ymparisto, aja


def ajo(ymp: Ymparisto) -> None:
    kanta = ymp.postgres()
    kanta.execute("DROP SCHEMA IF EXISTS luku02 CASCADE")
    kanta.execute("CREATE SCHEMA luku02")
    kanta.execute("SET search_path TO luku02")
    # @alku normalisoitu
    kanta.execute("""
        CREATE TABLE tuote (id text PRIMARY KEY, nimi text, hinta numeric);
        CREATE TABLE tilaus (id text PRIMARY KEY, asiakas text,
                             kaupunki text);
        CREATE TABLE rivi (tilaus text REFERENCES tilaus,
                           tuote text REFERENCES tuote,
                           kpl int, hinta numeric,
                           PRIMARY KEY (tilaus, tuote))""")
    # @loppu normalisoitu
    with kanta.cursor() as k:
        k.executemany("INSERT INTO tuote VALUES (%s, %s, %s)",
                      [(t["_id"], t["nimi"], t["hinta"]) for t in TUOTTEET])
        for t in TILAUKSET:
            k.execute("INSERT INTO tilaus VALUES (%s, %s, %s)",
                      (t["_id"], t["asiakas"], t["kaupunki"]))
            k.executemany("INSERT INTO rivi VALUES (%s, %s, %s, %s)",
                          [(t["_id"], r["tuote"], r["kpl"], r["hinta"])
                           for r in t["rivit"]])
    kanta.execute("CREATE TABLE dokumentti (id text PRIMARY KEY, "
                  "data jsonb)")
    with kanta.cursor() as k:
        k.executemany("INSERT INTO dokumentti VALUES (%s, %s)",
                      [(t["_id"], json.dumps(t)) for t in TILAUKSET])

    # @alku nakyma
    rivit = kanta.execute("""
        SELECT t.id, t.asiakas, tu.nimi, r.kpl
        FROM tilaus t JOIN rivi r ON r.tilaus = t.id
                      JOIN tuote tu ON tu.id = r.tuote
        WHERE t.id = 'T1' ORDER BY tu.nimi""").fetchall()
    for rivi in rivit:
        print("normalisoitu (3 taulua):", rivi)
    dokumentti = kanta.execute(
        "SELECT data FROM dokumentti WHERE id = 'T1'").fetchone()
    print("dokumentti, 1 haku:",
          [r["tuote"] for r in dokumentti[0]["rivit"]] if dokumentti
          else None)
    # @loppu nakyma

    # @alku toisinpain
    print("lamppuja myyty, normalisoitu:", kanta.execute(
        "SELECT sum(kpl) FROM rivi WHERE tuote = 'lamppu'").fetchone())
    print("lamppuja myyty, dokumentti:", kanta.execute("""
        SELECT sum((r ->> 'kpl')::int)
        FROM dokumentti, jsonb_array_elements(data -> 'rivit') r
        WHERE r ->> 'tuote' = 'lamppu'""").fetchone())
    # @loppu toisinpain

    # @alku muutos
    kanta.execute("UPDATE tuote SET nimi = 'LED-otsalamppu' "
                  "WHERE id = 'lamppu'")
    print("nimi muuttui kaikkialle:", kanta.execute(
        "SELECT DISTINCT tu.nimi FROM rivi r JOIN tuote tu "
        "ON tu.id = r.tuote WHERE r.tuote = 'lamppu'").fetchall())
    # @loppu muutos
    kanta.execute("RESET search_path")


if __name__ == "__main__":
    aja(ajo)

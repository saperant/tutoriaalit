"""Aikasarja Cassandrassa: partitio anturin ja päivän mukaan."""

import datetime as dt

from nosql.kontit import Ymparisto, aja


def ajo(ymp: Ymparisto) -> None:
    s = ymp.cassandra()
    s.execute("DROP KEYSPACE IF EXISTS kauppa07a")
    s.execute("""CREATE KEYSPACE kauppa07a WITH replication =
                 {'class': 'SimpleStrategy', 'replication_factor': 1}""")
    s.set_keyspace("kauppa07a")
    # @alku taulu
    s.execute("""
        CREATE TABLE mittaukset (
            anturi  text,
            paiva   date,
            aika    timestamp,
            arvo    double,
            PRIMARY KEY ((anturi, paiva), aika)
        ) WITH CLUSTERING ORDER BY (aika DESC)
          AND default_time_to_live = 2592000""")      # 30 vrk
    # @loppu taulu

    # @alku lisays
    lisays = s.prepare("INSERT INTO mittaukset (anturi, paiva, aika, "
                       "arvo) VALUES (?, ?, ?, ?)")
    alku = dt.datetime(2026, 11, 23, 22, 0, tzinfo=dt.UTC)
    for anturi in ["varasto-1", "varasto-2"]:
        for minuutti in range(0, 240, 10):       # neljä tuntia
            aika = alku + dt.timedelta(minutes=minuutti)
            arvo = 4.0 + (minuutti % 60) / 30 + (anturi == "varasto-2")
            s.execute(lisays, (anturi, aika.date(), aika, arvo))
    # @loppu lisays

    # @alku haku
    uusin = s.execute("""SELECT aika, arvo FROM mittaukset
                         WHERE anturi = 'varasto-1'
                         AND paiva = '2026-11-24' LIMIT 1""").one()
    print("uusin:", uusin.aika.strftime("%H:%M"), f"{uusin.arvo:.2f}")
    rivit = s.execute("""SELECT avg(arvo), max(arvo), count(*)
                         FROM mittaukset
                         WHERE anturi = 'varasto-1'
                         AND paiva = '2026-11-24'
                         AND aika >= '2026-11-24 00:00:00+0000'
                         AND aika < '2026-11-24 01:00:00+0000'""").one()
    print(f"klo 00-01: ka {rivit[0]:.2f}, max {rivit[1]:.2f}, "
          f"{rivit[2]} mittausta")
    for paiva in ["2026-11-23", "2026-11-24"]:
        maara = s.execute("SELECT count(*) FROM mittaukset WHERE anturi "
                          "= 'varasto-1' AND paiva = %s",
                          (dt.date.fromisoformat(paiva),)).one()[0]
        print(f"partitio (varasto-1, {paiva}): {maara} rivia")
    # @loppu haku


if __name__ == "__main__":
    aja(ajo)

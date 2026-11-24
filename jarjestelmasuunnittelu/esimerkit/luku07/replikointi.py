"""Lukureplika, replikointiviive ja lue omat kirjoituksesi.

PostgreSQL-ensisijainen ja suoratoistoreplika, joka soveltaa
muutokset kahden sekunnin viiveellä (recovery_min_apply_delay).
Tuotannossa viive syntyy kuormasta, verkosta tai pitkistä kyselyistä;
tässä se on asetettu, jotta ilmiö näkyy joka ajolla.
"""

import time

import psycopg

from jarjestelma.ymparisto import Postgres, Ymparisto, odota

VIIVE = "2s"


def yhteys(pg: Postgres) -> psycopg.Connection[tuple[object, ...]]:
    return psycopg.connect(host="127.0.0.1", port=pg.portti,
                           user="tutoriaali", dbname="postgres",
                           autocommit=True)


def saldo(c: psycopg.Connection[tuple[object, ...]]) -> object:
    rivi = c.execute("SELECT saldo FROM tili WHERE id = 1").fetchone()
    return rivi[0] if rivi else None


def main() -> None:
    with Ymparisto() as ymp:
        ensi = ymp.postgres()
        replika = ymp.replika(ensi, VIIVE)
        with yhteys(ensi) as e, yhteys(replika) as r:
            def tila() -> object:
                return e.execute("SELECT state, sync_state FROM"
                                 " pg_stat_replication").fetchone()
            odota(lambda: tila() == ("streaming", "async"),
                  "replika yhdistää")
            print("replikointi:", tila())
            e.execute("CREATE TABLE tili (id int PRIMARY KEY, saldo int)")
            e.execute("INSERT INTO tili VALUES (1, 100)")
            odota(lambda: r.execute("SELECT to_regclass('tili')")
                  .fetchone() != (None,) and saldo(r) == 100,
                  "replika saa tilin")

            # @alku vanhentunut
            e.execute("UPDATE tili SET saldo = 50 WHERE id = 1")
            print("ensisijainen heti päivityksen jälkeen:", saldo(e))
            print("replika heti päivityksen jälkeen:     ", saldo(r))
            # @loppu vanhentunut

            # @alku omat
            # Lue omat kirjoituksesi: kirjoituksen jälkeen otetaan talteen
            # WAL-sijainti, ja replikalta luetaan vasta, kun se on
            # soveltanut muutokset siihen asti. Sijainnin voi kuljettaa
            # istunnossa tai evästeessä.
            e.execute("UPDATE tili SET saldo = 70 WHERE id = 1")
            rivi = e.execute("SELECT pg_current_wal_lsn()").fetchone()
            if rivi is None:
                raise RuntimeError("WAL-sijaintia ei saatu")
            sijainti = rivi[0]
            odota(lambda: r.execute(
                "SELECT pg_last_wal_replay_lsn() >= %s::pg_lsn",
                (sijainti,)).fetchone() == (True,), "replika kiinni")
            print("replika, kun se on saavuttanut sijainnin:", saldo(r))
            # @loppu omat

            try:
                r.execute("UPDATE tili SET saldo = 0 WHERE id = 1")
            except psycopg.errors.ReadOnlySqlTransaction as virhe:
                print("kirjoitus replikaan:", virhe.sqlstate,
                      type(virhe).__name__)

            # @alku synkroninen
            # Synkroninen replikointi tasolla remote_apply: kirjoitus
            # palaa vasta, kun replika on soveltanut sen. Luku replikalta
            # on silloin aina tuore, mutta jokainen kirjoitus maksaa
            # replikan viiveen (PACELC: latenssi vastaan konsistenssi).
            e.execute("ALTER SYSTEM SET synchronous_standby_names = '*'")
            e.execute("SELECT pg_reload_conf()")
            odota(lambda: tila() == ("streaming", "sync"),
                  "replika synkroninen")    # asetus latautuu viiveellä
            e.execute("SET synchronous_commit = remote_apply")
            alku = time.monotonic()
            e.execute("UPDATE tili SET saldo = 90 WHERE id = 1")
            kesto = time.monotonic() - alku
            print("synkroninen kirjoitus odotti replikaa:", kesto > 1.5)
            print("replika heti synkronisen kirjoituksen jälkeen:", saldo(r))
            # @loppu synkroninen


if __name__ == "__main__":
    main()

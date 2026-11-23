"""Skeeman versiointi PRAGMA user_versionilla."""

import sqlite3

# @alku migraatiot
# Kukin migraatio ajetaan kerran ja järjestyksessä. Valmiita
# migraatioita ei muokata: muutos tehdään aina uutena migraationa.
MIGRAATIOT = [
    """CREATE TABLE asiakas (
           id   INTEGER PRIMARY KEY,
           nimi TEXT NOT NULL
       ) STRICT;""",
    """ALTER TABLE asiakas ADD COLUMN sahkoposti TEXT;
       CREATE UNIQUE INDEX asiakas_sahkoposti
           ON asiakas (lower(sahkoposti));""",
]


def migroi(yhteys: sqlite3.Connection) -> int:
    """Vie tietokannan uusimpaan versioon ja palauttaa ajettujen määrän."""
    versio = int(yhteys.execute("PRAGMA user_version").fetchone()[0])
    for numero, sql in enumerate(MIGRAATIOT[versio:], start=versio + 1):
        try:
            yhteys.executescript(
                f"BEGIN;\n{sql}\nPRAGMA user_version = {numero};\nCOMMIT;")
        except sqlite3.Error:
            if yhteys.in_transaction:
                yhteys.execute("ROLLBACK")
            raise
    return len(MIGRAATIOT) - versio
# @loppu migraatiot


def main() -> None:
    yhteys = sqlite3.connect("kauppa.db", autocommit=True)
    print("ajettiin:", migroi(yhteys))
    print("ajettiin uudelleen:", migroi(yhteys))
    (versio,) = yhteys.execute("PRAGMA user_version").fetchone()
    sarakkeet = [r[1] for r in yhteys.execute("PRAGMA table_info(asiakas)")]
    print("versio:", versio, "sarakkeet:", sarakkeet)
    yhteys.close()


if __name__ == "__main__":
    main()

"""N+1-kyselyt: kyselyjen laskeminen jäljityskutsulla."""

import sqlite3


def avaa() -> sqlite3.Connection:
    yhteys = sqlite3.connect(":memory:", autocommit=True)
    yhteys.executescript("""
        CREATE TABLE asiakas (id INTEGER PRIMARY KEY, nimi TEXT NOT NULL)
            STRICT;
        CREATE TABLE tilaus (
            id INTEGER PRIMARY KEY,
            asiakas_id INTEGER NOT NULL REFERENCES asiakas (id),
            summa_snt INTEGER NOT NULL
        ) STRICT;
        CREATE INDEX tilaus_asiakas ON tilaus (asiakas_id);
        INSERT INTO asiakas (nimi) VALUES
            ('Aino'), ('Matti'), ('Liisa'), ('Juha'), ('Sari');
        INSERT INTO tilaus (asiakas_id, summa_snt) VALUES
            (1, 2097), (1, 2490), (2, 8446), (3, 3490), (4, 4194),
            (2, 4980);
    """)
    return yhteys


# @alku n-plus-1
def summat_n_plus_1(yhteys: sqlite3.Connection) -> dict[str, int]:
    tulos = {}
    for asiakas_id, nimi in yhteys.execute(
            "SELECT id, nimi FROM asiakas ORDER BY id").fetchall():
        (summa,) = yhteys.execute(
            "SELECT coalesce(sum(summa_snt), 0) FROM tilaus "
            "WHERE asiakas_id = ?", (asiakas_id,)).fetchone()
        tulos[nimi] = summa
    return tulos
# @loppu n-plus-1


# @alku liitos
def summat(yhteys: sqlite3.Connection) -> dict[str, int]:
    rivit = yhteys.execute("""
        SELECT a.nimi, coalesce(sum(t.summa_snt), 0)
        FROM asiakas AS a
        LEFT JOIN tilaus AS t ON t.asiakas_id = a.id
        GROUP BY a.id
        ORDER BY a.id""")
    return dict(rivit.fetchall())
# @loppu liitos


def main() -> None:
    yhteys = avaa()
    # @alku laskuri
    kyselyt: list[str] = []
    yhteys.set_trace_callback(kyselyt.append)
    # @loppu laskuri
    a = summat_n_plus_1(yhteys)
    print(f"N+1: {len(kyselyt)} kyselyä")
    kyselyt.clear()
    b = summat(yhteys)
    print(f"liitos: {len(kyselyt)} kysely")
    yhteys.set_trace_callback(None)
    print("sama tulos:", a == b)
    yhteys.close()


if __name__ == "__main__":
    main()

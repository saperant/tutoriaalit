"""Transaktiot Pythonista: with-lohko sitoo tai peruu."""

import sqlite3


def avaa() -> sqlite3.Connection:
    # autocommit=False: moduuli avaa transaktion aina valmiiksi, ja
    # commit() tai rollback() päättää sen (PEP 249 -käytös).
    yhteys = sqlite3.connect(":memory:", autocommit=False)
    yhteys.execute("PRAGMA foreign_keys = ON")
    yhteys.execute("""
        CREATE TABLE tili (
            id    INTEGER PRIMARY KEY,
            omistaja TEXT NOT NULL,
            saldo_snt INTEGER NOT NULL CHECK (saldo_snt >= 0)
        ) STRICT""")
    yhteys.executemany(
        "INSERT INTO tili (id, omistaja, saldo_snt) VALUES (?, ?, ?)",
        [(1, "Aino", 10_000), (2, "Matti", 2_500)])
    yhteys.commit()
    return yhteys


# @alku siirto
def siirra(yhteys: sqlite3.Connection, lahde: int, kohde: int,
           summa_snt: int) -> None:
    """Siirtää rahaa tililtä toiselle; kaikki tai ei mitään."""
    with yhteys:  # onnistuessa commit, poikkeuksessa rollback
        yhteys.execute(
            "UPDATE tili SET saldo_snt = saldo_snt + ? WHERE id = ?",
            (summa_snt, kohde))
        yhteys.execute(
            "UPDATE tili SET saldo_snt = saldo_snt - ? WHERE id = ?",
            (summa_snt, lahde))
# @loppu siirto


def saldot(yhteys: sqlite3.Connection) -> str:
    rivit = yhteys.execute(
        "SELECT omistaja, saldo_snt FROM tili ORDER BY id")
    return ", ".join(f"{nimi} {snt / 100:.2f}" for nimi, snt in rivit)


def main() -> None:
    yhteys = avaa()
    # @alku kaytto
    siirra(yhteys, 1, 2, 3_000)
    print("siirron jälkeen:", saldot(yhteys))
    try:
        siirra(yhteys, 2, 1, 9_000)  # Matilla ei ole katetta
    except sqlite3.IntegrityError as virhe:
        print("peruttu:", virhe)
    print("perumisen jälkeen:", saldot(yhteys))
    # @loppu kaytto
    yhteys.close()


if __name__ == "__main__":
    main()

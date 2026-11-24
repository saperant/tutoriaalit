"""Kilpailutilanne liiketoimintalogiikassa: kaksi yhtäaikaista nostoa."""

import sqlite3

db = sqlite3.connect(":memory:", isolation_level=None)
db.execute("CREATE TABLE tili (id INTEGER PRIMARY KEY, saldo INTEGER)")


def alusta() -> None:
    db.execute("INSERT OR REPLACE INTO tili VALUES (1, 100)")


# @alku haavoittuva
# Kaksi pyyntöä lukee saldon ennen kuin kumpikaan kirjoittaa. Tässä
# lomitus tehdään käsin, jotta tulos on toistettava.
alusta()
saldo_a = db.execute("SELECT saldo FROM tili WHERE id = 1").fetchone()[0]
saldo_b = db.execute("SELECT saldo FROM tili WHERE id = 1").fetchone()[0]
for saldo in (saldo_a, saldo_b):
    if saldo >= 80:                                     # tarkistus
        db.execute("UPDATE tili SET saldo = saldo - 80 WHERE id = 1")
print("luku–tarkistus–kirjoitus:",
      db.execute("SELECT saldo FROM tili").fetchone()[0])
# @loppu haavoittuva


# @alku korjattu
def nosta(maara: int) -> bool:
    """Ehto ja muutos samassa lauseessa: tietokanta tekee ne atomisesti."""
    kursori = db.execute(
        "UPDATE tili SET saldo = saldo - ? WHERE id = 1 AND saldo >= ?",
        (maara, maara))
    return kursori.rowcount == 1
# @loppu korjattu


alusta()
print("ehdollinen päivitys:", nosta(80), nosta(80),
      db.execute("SELECT saldo FROM tili").fetchone()[0])

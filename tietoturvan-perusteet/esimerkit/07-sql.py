"""SQL-injektio: merkkijonoista koottu kysely ja parametrisoitu kysely."""

import hashlib
import sqlite3

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE kayttaja (nimi TEXT PRIMARY KEY, tiiviste TEXT)")
# Lyhyyden vuoksi tiivisteenä on SHA-256; oikeasti scrypt (luku 4).
db.execute("INSERT INTO kayttaja VALUES (?, ?)",
           ("aino", hashlib.sha256(b"salainen").hexdigest()))


# @alku haavoittuva
def kirjaudu_haavoittuva(nimi: str, salasana: str) -> bool:
    tiiviste = hashlib.sha256(salasana.encode()).hexdigest()
    kysely = (f"SELECT count(*) FROM kayttaja "          # noqa: S608
              f"WHERE nimi = '{nimi}' AND tiiviste = '{tiiviste}'")
    return bool(db.execute(kysely).fetchone()[0])
# @loppu haavoittuva


# @alku korjattu
def kirjaudu(nimi: str, salasana: str) -> bool:
    tiiviste = hashlib.sha256(salasana.encode()).hexdigest()
    rivi = db.execute(
        "SELECT count(*) FROM kayttaja WHERE nimi = ? AND tiiviste = ?",
        (nimi, tiiviste)).fetchone()
    return bool(rivi[0])
# @loppu korjattu


hyokkays = "aino' --"     # loppuosa kyselystä muuttuu kommentiksi
print("haavoittuva, oikea salasana:", kirjaudu_haavoittuva("aino",
                                                            "salainen"))
print("haavoittuva, hyökkäys:", kirjaudu_haavoittuva(hyokkays, "x"))
print("parametrisoitu, oikea salasana:", kirjaudu("aino", "salainen"))
print("parametrisoitu, hyökkäys:", kirjaudu(hyokkays, "x"))

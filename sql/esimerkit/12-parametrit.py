"""Parametrisoidut kyselyt ja SQL-injektion torjunta."""

import sqlite3


def avaa() -> sqlite3.Connection:
    yhteys = sqlite3.connect(":memory:", autocommit=False)
    yhteys.execute("""
        CREATE TABLE asiakas (
            id       INTEGER PRIMARY KEY,
            nimi     TEXT NOT NULL,
            kaupunki TEXT
        ) STRICT""")
    yhteys.executemany(
        "INSERT INTO asiakas (nimi, kaupunki) VALUES (?, ?)",
        [("Aino Virtanen", "Helsinki"), ("Matti Korhonen", "Tampere"),
         ("Liisa Nieminen", "Oulu")])
    yhteys.commit()
    return yhteys


# @alku vaara
def hae_vaarallinen(yhteys: sqlite3.Connection, nimi: str) -> list[str]:
    # VÄÄRIN: syöte liitetään SQL-tekstiin.
    sql = f"SELECT nimi FROM asiakas WHERE nimi = '{nimi}'"
    return [rivi[0] for rivi in yhteys.execute(sql)]
# @loppu vaara


# @alku oikein
def hae(yhteys: sqlite3.Connection, nimi: str) -> list[str]:
    # Oikein: arvo kulkee erillään SQL-tekstistä paikkamerkin kautta.
    rivit = yhteys.execute(
        "SELECT nimi FROM asiakas WHERE nimi = ?", (nimi,))
    return [rivi[0] for rivi in rivit]
# @loppu oikein


# @alku lista
def hae_kaupungeista(yhteys: sqlite3.Connection,
                     kaupungit: list[str]) -> list[str]:
    # IN-listaan yksi paikkamerkki kutakin arvoa kohden.
    merkit = ", ".join("?" * len(kaupungit))
    sql = f"SELECT nimi FROM asiakas WHERE kaupunki IN ({merkit})"
    return [rivi[0] for rivi in yhteys.execute(sql, kaupungit)]
# @loppu lista


# @alku tunniste
JARJESTYS = {"nimi": "nimi", "kaupunki": "kaupunki, nimi"}


def listaa(yhteys: sqlite3.Connection, jarjestys: str) -> list[str]:
    # Tunnisteita ei voi parametrisoida: valitaan sallittujen joukosta.
    try:
        sarakkeet = JARJESTYS[jarjestys]
    except KeyError:
        raise ValueError(f"tuntematon järjestys: {jarjestys!r}") from None
    sql = f"SELECT nimi FROM asiakas ORDER BY {sarakkeet}"
    return [rivi[0] for rivi in yhteys.execute(sql)]
# @loppu tunniste


def main() -> None:
    yhteys = avaa()
    hyokkays = "' OR '1'='1"
    print("vaarallinen:", hae_vaarallinen(yhteys, hyokkays))
    print("parametrisoitu:", hae(yhteys, hyokkays))
    print("kaupungeista:", hae_kaupungeista(yhteys, ["Oulu", "Tampere"]))
    print("järjestys:", listaa(yhteys, "kaupunki"))
    try:
        listaa(yhteys, "nimi; DROP TABLE asiakas")
    except ValueError as virhe:
        print("hylätty:", virhe)
    yhteys.close()


if __name__ == "__main__":
    main()

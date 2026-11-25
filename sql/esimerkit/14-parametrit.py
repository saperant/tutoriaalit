"""Arvot kyselyyn parametreina, ja mitä tapahtuu, jos ne liimataan
SQL-tekstiin."""

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
         ("Liisa Nieminen", "Oulu"), ("Mia O'Connor", "Turku")])
    yhteys.commit()
    return yhteys


# @alku oikein
def hae(yhteys: sqlite3.Connection, nimi: str) -> list[str]:
    # Arvo kulkee erillään SQL-tekstistä paikkamerkin kautta.
    rivit = yhteys.execute(
        "SELECT nimi FROM asiakas WHERE nimi = ?", (nimi,))
    return [rivi[0] for rivi in rivit]
# @loppu oikein


# @alku nimetty
def hae_kaupungista(yhteys: sqlite3.Connection, kaupunki: str,
                    alku: str) -> list[str]:
    # Nimetyt parametrit: sama arvo voi esiintyä monessa kohdassa.
    rivit = yhteys.execute(
        """SELECT nimi FROM asiakas
           WHERE kaupunki = :kaupunki AND nimi LIKE :alku || '%'
           ORDER BY nimi""",
        {"kaupunki": kaupunki, "alku": alku})
    return [rivi[0] for rivi in rivit]
# @loppu nimetty


# @alku liimaus
def liimattu_sql(nimi: str) -> str:
    # VÄÄRIN: arvo liitetään SQL-tekstiin.
    return f"SELECT nimi FROM asiakas WHERE nimi = '{nimi}'"


def hae_liimaten(yhteys: sqlite3.Connection, nimi: str) -> list[str]:
    return [rivi[0] for rivi in yhteys.execute(liimattu_sql(nimi))]
# @loppu liimaus


# @alku lista
def hae_kaupungeista(yhteys: sqlite3.Connection,
                     kaupungit: list[str]) -> list[str]:
    # IN-listaan yksi paikkamerkki kutakin arvoa kohden.
    merkit = ", ".join("?" * len(kaupungit))
    sql = f"""SELECT nimi FROM asiakas WHERE kaupunki IN ({merkit})
              ORDER BY nimi"""
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
    # @alku kaytto
    print("parametrilla:", hae(yhteys, "Mia O'Connor"))
    print("nimetyillä:", hae_kaupungista(yhteys, "Helsinki", "A"))
    # @loppu kaytto

    # @alku hajoaa
    # Liimattu kysely hajoaa jo tavalliseen heittomerkkiin...
    print("SQL:", liimattu_sql("Mia O'Connor"))
    try:
        hae_liimaten(yhteys, "Mia O'Connor")
    except sqlite3.OperationalError as virhe:
        print("virhe:", type(virhe).__name__)
    # ...ja sopivasti valittu syöte muuttaa kyselyn merkityksen.
    hyokkays = "' OR '1'='1"
    print("SQL:", liimattu_sql(hyokkays))
    print("liimaten:", len(hae_liimaten(yhteys, hyokkays)), "riviä")
    print("parametrilla:", len(hae(yhteys, hyokkays)), "riviä")
    # @loppu hajoaa

    print("kaupungeista:", hae_kaupungeista(yhteys, ["Oulu", "Tampere"]))
    print("järjestys:", listaa(yhteys, "kaupunki"))
    try:
        listaa(yhteys, "nimi; DROP TABLE asiakas")
    except ValueError as virhe:
        print("hylätty:", virhe)
    yhteys.close()


if __name__ == "__main__":
    main()

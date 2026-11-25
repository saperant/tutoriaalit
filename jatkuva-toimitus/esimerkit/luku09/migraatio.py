"""Skeemamuutos ilman käyttökatkoa: laajenna, siirrä, supista.

Sarake nimi jaetaan kahdeksi sarakkeeksi. Rullaavassa päivityksessä
vanha ja uusi sovellusversio käyttävät samaa tietokantaa yhtä aikaa,
joten jokaisen välitilan on kelvattava molemmille.
"""

import sqlite3
from collections.abc import Callable

Yhteys = sqlite3.Connection


# @alku versiot
class V1:
    """Alkuperäinen sovellus: tuntee vain sarakkeen nimi."""

    def lisaa(self, kanta: Yhteys, etu: str, suku: str) -> None:
        kanta.execute("INSERT INTO asiakas (nimi) VALUES (?)",
                      (f"{etu} {suku}",))

    def lue(self, kanta: Yhteys) -> list[str | None]:
        return [r[0] for r in kanta.execute(
            "SELECT nimi FROM asiakas ORDER BY id")]


class V2(V1):
    """Siirtymäversio: kirjoittaa vanhaan ja uuteen, lukee yhä vanhaa."""

    def lisaa(self, kanta: Yhteys, etu: str, suku: str) -> None:
        kanta.execute("INSERT INTO asiakas (nimi, etunimi, sukunimi) "
                      "VALUES (?, ?, ?)", (f"{etu} {suku}", etu, suku))


class V3(V2):
    """Lukee uusia sarakkeita, kirjoittaa vielä molempiin."""

    def lue(self, kanta: Yhteys) -> list[str | None]:
        return [None if etu is None else f"{etu} {suku}"
                for etu, suku in kanta.execute(
                    "SELECT etunimi, sukunimi FROM asiakas ORDER BY id")]


class V4(V3):
    """Lopullinen sovellus: vanhaa saraketta ei enää ole sen maailmassa."""

    def lisaa(self, kanta: Yhteys, etu: str, suku: str) -> None:
        kanta.execute("INSERT INTO asiakas (etunimi, sukunimi) "
                      "VALUES (?, ?)", (etu, suku))
# @loppu versiot


# @alku migraatiot
def laajenna(kanta: Yhteys) -> None:
    kanta.execute("ALTER TABLE asiakas ADD COLUMN etunimi TEXT")
    kanta.execute("ALTER TABLE asiakas ADD COLUMN sukunimi TEXT")


def tayta(kanta: Yhteys) -> None:
    """Täyttää vanhat rivit. Suuressa taulussa tämä tehdään erissä."""
    kanta.execute(
        "UPDATE asiakas SET etunimi = substr(nimi, 1, instr(nimi, ' ') - 1),"
        " sukunimi = substr(nimi, instr(nimi, ' ') + 1) "
        "WHERE etunimi IS NULL")


def supista(kanta: Yhteys) -> None:
    kanta.execute("ALTER TABLE asiakas DROP COLUMN nimi")
# @loppu migraatiot


def uusi_kanta() -> Yhteys:
    kanta = sqlite3.connect(":memory:")
    kanta.execute("CREATE TABLE asiakas (id INTEGER PRIMARY KEY, nimi TEXT)")
    V1().lisaa(kanta, "Aino", "Aalto")
    return kanta


def kokeile(kanta: Yhteys, vaihe: str, versiot: list[V1]) -> bool:
    """Jokainen ajossa oleva versio lisää rivin ja lukee kaikki rivit."""
    rivit = kanta.execute("SELECT count(*) FROM asiakas").fetchone()[0]
    tilat = []
    for versio in versiot:
        nimi = type(versio).__name__
        try:
            versio.lisaa(kanta, "Uusi", f"Asiakas{rivit}")
            rivit += 1
            luettu = versio.lue(kanta)
            ok = len(luettu) == rivit and None not in luettu
            tilat.append(f"{nimi} {'ok' if ok else 'PUUTTUU TIETOJA'}")
        except sqlite3.Error as virhe:
            tilat.append(f"{nimi} VIRHE ({type(virhe).__name__})")
    print(f"  {vaihe:<28}{', '.join(tilat)}")
    return all(tila.endswith(" ok") for tila in tilat)


# @alku polku
Askel = tuple[str, Callable[[Yhteys], None] | None, list[V1]]
POLKU: list[Askel] = [
    ("alku", None, [V1()]),
    ("laajenna skeema", laajenna, [V1()]),
    ("V2 käyttöön rullaten", None, [V1(), V2()]),
    ("V2 kaikkialla, täytä rivit", tayta, [V2()]),
    ("V3 käyttöön rullaten", None, [V2(), V3()]),
    ("V4 käyttöön rullaten", None, [V3(), V4()]),
    ("supista skeema", supista, [V4()]),
]
# @loppu polku

print("laajenna, siirrä, supista:")
kanta = uusi_kanta()
for vaihe, migraatio, versiot in POLKU:
    if migraatio:
        migraatio(kanta)
    assert kokeile(kanta, vaihe, versiot)

print("kaikki kerralla, vanha versio vielä ajossa:")
kanta = uusi_kanta()
laajenna(kanta)
tayta(kanta)
supista(kanta)
kokeile(kanta, "yksi migraatio", [V1(), V4()])

print("väärä järjestys: uusi lukija ennen täyttöä:")
kanta = uusi_kanta()
laajenna(kanta)
kokeile(kanta, "V3 ennen täyttöä", [V1(), V3()])

print("supistus liian aikaisin: V3 kirjoittaa vielä vanhaan:")
kanta = uusi_kanta()
laajenna(kanta)
tayta(kanta)
supista(kanta)
kokeile(kanta, "V3 ja V4 ajossa", [V3(), V4()])

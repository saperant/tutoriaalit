"""DAO eli tietovarasto: tietokantakoodi yhden rajapinnan taakse.

Palvelukerros käyttää rajapintaa (Protocol), ei SQL:ää. Sama palvelu
toimii SQLite-toteutuksella ja muistissa olevalla testitoteutuksella.
"""

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from typing import Protocol


# @alku rajapinta
@dataclass(frozen=True)
class Tuote:
    koodi: str
    nimi: str
    hinta: int  # senteissä


class TuoteVarasto(Protocol):
    def hae(self, koodi: str) -> Tuote | None: ...
    def tallenna(self, tuote: Tuote) -> None: ...
    def halvimmat(self, n: int) -> list[Tuote]: ...
# @loppu rajapinta


# @alku sqlite
class SqliteTuoteVarasto:
    """Kaikki tuotteiden SQL on tässä luokassa ja vain tässä."""

    def __init__(self, yhteys: sqlite3.Connection) -> None:
        self._db = yhteys
        self._db.execute("""CREATE TABLE IF NOT EXISTS tuote (
            koodi TEXT PRIMARY KEY, nimi TEXT NOT NULL,
            hinta INTEGER NOT NULL CHECK (hinta >= 0)) STRICT""")

    def hae(self, koodi: str) -> Tuote | None:
        rivi = self._db.execute(
            "SELECT koodi, nimi, hinta FROM tuote WHERE koodi = ?",
            (koodi,)).fetchone()
        return Tuote(*rivi) if rivi else None

    def tallenna(self, tuote: Tuote) -> None:
        self._db.execute(
            """INSERT INTO tuote (koodi, nimi, hinta) VALUES (?, ?, ?)
               ON CONFLICT (koodi) DO UPDATE
               SET nimi = excluded.nimi, hinta = excluded.hinta""",
            (tuote.koodi, tuote.nimi, tuote.hinta))

    def halvimmat(self, n: int) -> list[Tuote]:
        rivit = self._db.execute(
            "SELECT koodi, nimi, hinta FROM tuote ORDER BY hinta, koodi "
            "LIMIT ?", (n,)).fetchall()
        return [Tuote(*r) for r in rivit]
# @loppu sqlite


# @alku muisti
class MuistiTuoteVarasto:
    """Testikaksoinen: nopea, mutta ei tarkista SQL:ää eikä rajoitteita."""

    def __init__(self) -> None:
        self._tuotteet: dict[str, Tuote] = {}

    def hae(self, koodi: str) -> Tuote | None:
        return self._tuotteet.get(koodi)

    def tallenna(self, tuote: Tuote) -> None:
        self._tuotteet[tuote.koodi] = tuote

    def halvimmat(self, n: int) -> list[Tuote]:
        return sorted(self._tuotteet.values(),
                      key=lambda t: (t.hinta, t.koodi))[:n]
# @loppu muisti


# @alku palvelu
def alennus(varasto: TuoteVarasto, koodi: str, prosentti: int) -> Tuote:
    """Palvelukerroksen sääntö: ei SQL:ää, vain rajapinnan kutsuja."""
    tuote = varasto.hae(koodi)
    if tuote is None:
        raise KeyError(koodi)
    uusi = Tuote(tuote.koodi, tuote.nimi,
                 tuote.hinta * (100 - prosentti) // 100)
    varasto.tallenna(uusi)
    return uusi
# @loppu palvelu


def kokeile(nimi: str, varasto: TuoteVarasto) -> None:
    for t in (Tuote("kahvi", "Kahvi 500 g", 590),
              Tuote("tee", "Tee 100 g", 450),
              Tuote("kaakao", "Kaakao 250 g", 380)):
        varasto.tallenna(t)
    alennus(varasto, "kahvi", 40)
    halvimmat = ", ".join(f"{t.koodi} {t.hinta}"
                          for t in varasto.halvimmat(2))
    print(f"{nimi}: {halvimmat}")


# @alku ero
def kokeile_virhetta(nimi: str, varasto: TuoteVarasto) -> None:
    """150 prosentin alennus tekisi hinnasta negatiivisen."""
    try:
        tuote = alennus(varasto, "tee", 150)
    except sqlite3.IntegrityError:
        print(f"{nimi}: rajoite hylkäsi hinnan")
    else:
        print(f"{nimi}: hyväksyi hinnan {tuote.hinta}")
# @loppu ero


def main() -> None:
    yhteys = sqlite3.connect(":memory:", autocommit=False)
    with closing(yhteys), yhteys:   # sulkeminen ja transaktio
        varasto = SqliteTuoteVarasto(yhteys)
        kokeile("SQLite", varasto)
        kokeile_virhetta("SQLite", varasto)
    muisti = MuistiTuoteVarasto()
    kokeile("muisti", muisti)
    kokeile_virhetta("muisti", muisti)


if __name__ == "__main__":
    main()

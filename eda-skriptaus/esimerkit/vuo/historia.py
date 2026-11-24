"""Regressiohistoria SQLite-tietokannassa: trendit ja epävakaat testit."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from vuo.malli import SimTulos
from vuo.regressio import allekirjoitus

# @alku skeema
SKEEMA = """
CREATE TABLE IF NOT EXISTS ajo (
    id        INTEGER PRIMARY KEY,
    versio    TEXT NOT NULL,      -- commit, jonka koodia ajettiin
    jarjestys INTEGER NOT NULL    -- versioiden järjestys historiassa
);
CREATE TABLE IF NOT EXISTS tulos (
    ajo           INTEGER NOT NULL REFERENCES ajo(id),
    testi         TEXT NOT NULL,
    siemen        INTEGER NOT NULL,
    tila          TEXT NOT NULL,
    allekirjoitus TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS tulos_testi ON tulos(testi, siemen);
"""


def avaa(polku: Path) -> sqlite3.Connection:
    yhteys = sqlite3.connect(polku)
    yhteys.executescript(SKEEMA)
    return yhteys


def kirjaa(yhteys: sqlite3.Connection, versio: str, jarjestys: int,
           tulokset: list[SimTulos]) -> int:
    """Yksi regressioajo yhtenä transaktiona."""
    with yhteys:
        kursori = yhteys.execute(
            "INSERT INTO ajo (versio, jarjestys) VALUES (?, ?)",
            (versio, jarjestys))
        ajo = kursori.lastrowid
        assert ajo is not None
        yhteys.executemany(
            "INSERT INTO tulos VALUES (?, ?, ?, ?, ?)",
            [(ajo, t.testi, t.siemen, t.tila, allekirjoitus(t))
             for t in tulokset])
    return ajo
# @loppu skeema


# @alku trendi
def trendi(yhteys: sqlite3.Connection) -> list[tuple[str, int, int]]:
    """Versio, läpäisseet ja kaikki: viimeisin ajo kustakin versiosta."""
    return yhteys.execute("""
        SELECT a.versio, SUM(t.tila = 'ok'), COUNT(*)
        FROM tulos t JOIN ajo a ON a.id = t.ajo
        WHERE a.id = (SELECT MAX(id) FROM ajo WHERE versio = a.versio)
        GROUP BY a.versio ORDER BY MIN(a.jarjestys)
    """).fetchall()
# @loppu trendi


# @alku epavakaat
def epavakaat(yhteys: sqlite3.Connection) -> list[tuple[str, int, str]]:
    """Testi ja siemen, jotka samalla koodilla sekä menivät läpi että
    hylättiin: tulos ei riipu koodista eikä siemenestä."""
    return yhteys.execute("""
        SELECT t.testi, t.siemen, a.versio
        FROM tulos t JOIN ajo a ON a.id = t.ajo
        GROUP BY a.versio, t.testi, t.siemen
        HAVING COUNT(DISTINCT t.tila = 'ok') = 2
        ORDER BY t.testi, t.siemen, MIN(a.jarjestys)
    """).fetchall()
# @loppu epavakaat


# @alku ensimmainen
def ensimmainen_hylkays(
        yhteys: sqlite3.Connection) -> list[tuple[str, str, int]]:
    """Kustakin virheallekirjoituksesta versio, jossa se nähtiin
    ensimmäisen kerran, ja montako kertaa se on nähty."""
    return yhteys.execute("""
        SELECT allekirjoitus, versio, maara FROM (
            SELECT t.allekirjoitus, a.versio,
                   COUNT(*) OVER (PARTITION BY t.allekirjoitus) AS maara,
                   ROW_NUMBER() OVER (PARTITION BY t.allekirjoitus
                                      ORDER BY a.jarjestys) AS n
            FROM tulos t JOIN ajo a ON a.id = t.ajo
            WHERE t.tila != 'ok')
        WHERE n = 1 ORDER BY allekirjoitus
    """).fetchall()
# @loppu ensimmainen

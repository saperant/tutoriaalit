"""Jäsentimien yksikkötestit tallennetuilla raporteilla.

Näyteraportti on testin syöte, joten jäsentimen voi testata ilman
työkalua. Kun työkalun versio vaihtuu, uusi raportti tallennetaan
näytteeksi ja testit kertovat, muuttuiko muoto.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from vuo.malli import SimTulos, Varoitus
from vuo.raportit import (RaporttiVirhe, lue_kattavuus, lue_simulointi,
                          lue_sta, lue_verilator, lue_yosys_stat)
from vuo.regressio import allekirjoitus
from vuo.varoitukset import Sallittu, luokittele

NAYTTEET = Path(__file__).resolve().parent.parent / "naytteet"


# @alku testit
def test_yosys_stat() -> None:
    res = lue_yosys_stat(NAYTTEET / "stat.json")
    assert (res.solut, res.kiikut) == (24, 9)


def test_sta_tarkistaa_slackin() -> None:
    assert lue_sta((NAYTTEET / "sta.txt").read_text()).slack == 8.27
    with pytest.raises(RaporttiVirhe, match="slack"):
        lue_sta((NAYTTEET / "sta_rikki.txt").read_text())


# @loppu testit


def test_sta_vajaa_raportti() -> None:
    with pytest.raises(RaporttiVirhe, match="puuttuu"):
        lue_sta("Ajoitusraportti (opetus-sta)\n")


def test_verilator_ohittaa_jatkorivit() -> None:
    varoitukset = lue_verilator((NAYTTEET / "lint.log").read_text())
    assert [v.koodi for v in varoitukset] == [
        "WIDTHTRUNC", "UNUSEDSIGNAL", "UNUSEDSIGNAL", "UNUSEDSIGNAL"]
    assert varoitukset[0].rivi == 16


# @alku testit2
@pytest.mark.parametrize("loki, tila", [
    ("TESTI OK 5 operaatiota\n", "ok"),
    ("VIRHE op=1\nTESTI EPÄONNISTUI 1 virhettä\n", "virhe"),
    ("$ ./sim\n\n*** aikakatkaisu 2 s\n", "aikakatkaisu"),
    ("Segmentation fault\n", "virhe"),
])
def test_simuloinnin_tila(loki: str, tila: str) -> None:
    assert lue_simulointi(loki, "t", 1).tila == tila
# @loppu testit2


def test_kattavuus() -> None:
    lokerot = lue_kattavuus((NAYTTEET / "sim.log").read_text())
    assert len(lokerot) == 16 and lokerot["op=3 a7=0 b7=0"] == 3


def test_allekirjoitus_sailyttaa_operaation() -> None:
    tulos = SimTulos("t", 1, "virhe", 1, ("VIRHE op=3 a=1 b=2 saatu=3",))
    assert allekirjoitus(tulos) == "VIRHE op=3 a=<n> b=<n> saatu=<n>"


def test_vanhentunut_sallinta() -> None:
    v = Varoitus("verilator", "UNUSEDSIGNAL", "a.sv", 1, "'x' unused")
    s = Sallittu("UNUSEDSIGNAL", "a.sv", "'x'", "syy", date(2026, 1, 1))
    assert luokittele([v], [s], date(2025, 12, 31)).lapi
    assert not luokittele([v], [s], date(2026, 1, 2)).lapi

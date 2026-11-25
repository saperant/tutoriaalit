"""Pytest-liitännäinen, joka kirjoittaa testien tulokset vakiomuodossa.

Pytestin oma tuloste sisältää kestoja ja polkuja, jotka vaihtelevat
ajosta toiseen. Tämä liitännäinen kirjoittaa ympäristömuuttujan
TULOSTIN_TIEDOSTO nimeämään tiedostoon yhden rivin testiä kohden, joten
tulosta voi verrata tallennettuun (ks. aja.py):

    ok    test_kori.py::test_tyhjan_korin_summa_on_nolla
    FAIL  test_kori.py::test_yhden_rivin_summa
          assert 0 == 500
    2 testiä: 1 ok, 1 epäonnistui

Yli 12 testin ajosta tulostetaan tiedostokohtainen yhteenveto ja vain
epäonnistuneet testit.
"""

from __future__ import annotations

import os
import textwrap
from pathlib import PurePosixPath
from typing import Any

import pytest

LEVEYS = 72
TIIVISTYSRAJA = 12   # tätä pidemmästä ajosta tulostetaan yhteenveto
_rivit: list[str] = []
_testit: list[tuple[str, str, list[str]]] = []
_laskuri = {"ok": 0, "FAIL": 0, "VIRHE": 0}


def _sisenna(teksti: str) -> list[str]:
    tulos: list[str] = []
    for rivi in teksti.splitlines():
        tulos += textwrap.wrap(rivi, LEVEYS, subsequent_indent="  ") or [""]
    return ["      " + r for r in tulos]


def _nimi(nodeid: str) -> str:
    """Testin tunniste ilman hakemistoa: test_kori.py::test_summa."""
    tiedosto, erotin, loput = nodeid.partition("::")
    return PurePosixPath(tiedosto).name + erotin + loput


def _viesti(report: Any) -> str:
    """Virheen ensimmäinen rivi ilman polkua ja rivinumeroa."""
    kaatuminen = getattr(report.longrepr, "reprcrash", None)
    if kaatuminen is not None:
        return str(kaatuminen.message).splitlines()[0]
    viimeinen = str(report.longrepr).strip().splitlines()[-1]
    return viimeinen.removeprefix("E").strip()


def _vastaesimerkki(report: Any) -> list[str]:
    """Hypothesiksen pienentämä vastaesimerkki, jos testi tuotti sen."""
    rivit: list[str] = [r.removeprefix("E").strip()
                        for r in report.longreprtext.splitlines()]
    alut = ("Failing test case:", "Falsifying example:")
    for i, rivi in enumerate(rivit):
        if not rivi.startswith(alut):
            continue
        loppu = i + 1
        while loppu < len(rivit) and rivit[loppu] and not \
                rivit[loppu].startswith(("Explanation", "You can", "_")):
            loppu += 1
            if rivit[loppu - 1] in (")", "state.teardown()"):
                break
        lohko = rivit[i:loppu]
        if lohko[0].endswith("(") and lohko[-1] == ")":
            # Funktiokutsu yhdelle riville: testi(a=1, b=2)
            argumentit = " ".join(lohko[1:-1]).rstrip(",")
            return [f"{lohko[0]}{argumentit})"]
        return lohko
    return []


def pytest_collectreport(report: pytest.CollectReport) -> None:
    if report.failed:
        _laskuri["VIRHE"] += 1
        _rivit.append(f"VIRHE {_nimi(report.nodeid)}")
        _rivit.extend(_sisenna(_viesti(report)))


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    epaonnistui = report.outcome == "failed"
    if report.when != "call" and not epaonnistui:
        return
    tulos = "FAIL" if epaonnistui else "ok"
    _laskuri[tulos] += 1
    lisarivit: list[str] = []
    if epaonnistui:
        lisarivit += _sisenna(_viesti(report))
        for rivi in _vastaesimerkki(report):
            lisarivit += _sisenna(rivi)
    _testit.append((tulos, _nimi(report.nodeid), lisarivit))


def _yhteenveto(ok: int, epaonnistui: int) -> str:
    osat = [f"{ok} ok"]
    if epaonnistui:
        osat.append(f"{epaonnistui} epäonnistui")
    return ", ".join(osat)


def _tiivis() -> list[str]:
    """Pitkä ajo: yhteenveto tiedostoittain ja vain epäonnistuneet."""
    rivit: list[str] = []
    tiedostot = list(dict.fromkeys(n.split("::")[0] for _, n, _ in _testit))
    for tiedosto in tiedostot:
        omat = [t for t in _testit if t[1].split("::")[0] == tiedosto]
        huonot = [t for t in omat if t[0] == "FAIL"]
        rivit.append(f"{tiedosto}: "
                     + _yhteenveto(len(omat) - len(huonot), len(huonot)))
        for tulos, nimi, lisarivit in huonot:
            rivit.append(f"{tulos:<5} {nimi.split('::', 1)[1]}")
            rivit.extend(lisarivit)
    return rivit


def pytest_sessionfinish(session: pytest.Session) -> None:
    if len(_testit) > TIIVISTYSRAJA:
        _rivit.extend(_tiivis())
    else:
        for tulos, nimi, lisarivit in _testit:
            _rivit.append(f"{tulos:<5} {nimi}")
            _rivit.extend(lisarivit)
    testeja = _laskuri["ok"] + _laskuri["FAIL"]
    yhteenveto = _yhteenveto(_laskuri["ok"], _laskuri["FAIL"])
    if _laskuri["VIRHE"]:
        yhteenveto += f", {_laskuri['VIRHE']} keräysvirhe"
    sana = "testi" if testeja == 1 else "testiä"
    _rivit.append(f"{testeja} {sana}: {yhteenveto}")
    with open(os.environ["TULOSTIN_TIEDOSTO"], "w", encoding="utf-8") as f:
        f.write("\n".join(_rivit) + "\n")

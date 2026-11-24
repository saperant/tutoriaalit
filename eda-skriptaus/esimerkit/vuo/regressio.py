"""Regressioajot: testilista, siemenet, rinnakkaisuus ja allekirjoitukset."""

from __future__ import annotations

import re
import tomllib
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from vuo.ajo import aja
from vuo.malli import SimTulos
from vuo.raportit import lue_simulointi


# @alku testi
@dataclass(frozen=True)
class Testi:
    nimi: str
    siemenet: tuple[int, ...]
    maara: int = 200
    aikaraja: float = 60.0
    maarittelyt: tuple[str, ...] = ()
    plusargit: tuple[str, ...] = ()


def lue_testilista(polku: Path) -> list[Testi]:
    data = tomllib.loads(polku.read_text(encoding="utf-8"))
    testit = []
    for t in data["testi"]:
        siemenet = t.get("siemenet") or range(1, t["siemenia"] + 1)
        testit.append(Testi(
            t["nimi"], tuple(siemenet), t.get("maara", 200),
            float(t.get("aikaraja", 60)), tuple(t.get("maarittelyt", [])),
            tuple(t.get("plusargit", []))))
    nimet = [t.nimi for t in testit]
    if len(set(nimet)) != len(nimet):
        raise ValueError("testilistassa on sama nimi kahdesti")
    return testit
# @loppu testi


# @alku kaanna
def kaanna(juuri: Path, ajohak: Path,
           maarittelyt: tuple[str, ...]) -> Path:
    """Yksi käännös kutakin makroyhdistelmää kohden: siemenet ajavat
    samaa ohjelmaa, joten kaikkea ei käännetä uudelleen."""
    nimi = "_".join(sorted(maarittelyt)) or "oletus"
    hak = ajohak / f"obj_{nimi}"
    tulos = aja(["verilator", "--binary", "-Wall", "--top-module", "alu_tb",
                 *(f"-D{m}" for m in sorted(maarittelyt)),
                 "-Mdir", str(hak), "-o", "sim",
                 str(juuri / "rtl" / "alu.sv"),
                 str(juuri / "tb" / "alu_tb.sv")],
                ajohak / "lokit" / f"kaannos_{nimi}.log")
    if not tulos.onnistui:
        raise RuntimeError(f"käännös {nimi} epäonnistui: {tulos.loki}")
    return hak / "sim"
# @loppu kaanna


# @alku regressio
def aja_regressio(juuri: Path, ajohak: Path, testit: list[Testi],
                  rinnakkain: int = 4) -> list[SimTulos]:
    yhdistelmat = sorted({t.maarittelyt for t in testit})
    with ThreadPoolExecutor(rinnakkain) as pooli:
        ohjelmat = dict(zip(yhdistelmat, pooli.map(
            lambda m: kaanna(juuri, ajohak, m), yhdistelmat), strict=True))

        def aja_yksi(testi: Testi, siemen: int) -> SimTulos:
            loki = ajohak / "lokit" / f"{testi.nimi}_{siemen}.log"
            aja([str(ohjelmat[testi.maarittelyt]), f"+siemen={siemen}",
                 f"+maara={testi.maara}", *testi.plusargit],
                loki, aikaraja=testi.aikaraja)
            return lue_simulointi(loki.read_text(encoding="utf-8"),
                                  testi.nimi, siemen)

        tyot = [pooli.submit(aja_yksi, t, s)
                for t in testit for s in t.siemenet]
        tulokset = [ty.result() for ty in tyot]
    return sorted(tulokset, key=lambda r: (r.testi, r.siemen))
# @loppu regressio


# @alku allekirjoitus
SAILYTETTAVAT = {"op"}


def allekirjoitus(tulos: SimTulos) -> str:
    """Virheen tunniste, jossa data-arvot on korvattu merkillä <n>.
    Sama allekirjoitus eri siemenillä on todennäköisesti sama vika."""
    if tulos.tila != "virhe":
        return tulos.tila
    rivi = tulos.viestit[0] if tulos.viestit else "ei viestiä"
    return re.sub(r"(\w+)=(\d+)",
                  lambda m: m[0] if m[1] in SAILYTETTAVAT
                  else f"{m[1]}=<n>", rivi)


def ryhmittele(tulokset: list[SimTulos]) -> dict[str, list[SimTulos]]:
    ryhmat: dict[str, list[SimTulos]] = defaultdict(list)
    for t in tulokset:
        if t.tila != "ok":
            ryhmat[allekirjoitus(t)].append(t)
    return dict(sorted(ryhmat.items(), key=lambda kv: -len(kv[1])))
# @loppu allekirjoitus

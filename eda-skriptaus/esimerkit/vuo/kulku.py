"""Tämän projektin suunnitteluvuo: lint, synteesi, ajoitus ja simulointi."""

from __future__ import annotations

import functools
import shutil
from pathlib import Path

from vuo.ajo import tyokaluversio
from vuo.vaiheet import Vaihe, Vuo


def tclsh() -> str:
    """Debianissa tulkki on nimellä tclsh8.6, muualla usein tclsh."""
    return shutil.which("tclsh8.6") or shutil.which("tclsh") or "tclsh"


# @alku versiot
# Kunkin työkalun versiokysely. Versio kuuluu vaiheen leimaan, joten
# työkalun päivitys ajaa vaiheen uudelleen.
VERSIOKOMENNOT = {"verilator": ["--version"], "yosys": ["-V"]}


@functools.cache
def versio(ohjelma: str) -> str:
    valitsimet = VERSIOKOMENNOT.get(Path(ohjelma).name)
    return tyokaluversio([ohjelma, *valitsimet]) if valitsimet else ""
# @loppu versiot


# @alku kulku
def projektin_vuo(juuri: Path, ajohak: Path, leveys: int = 8,
                  jakso: float = 10.0) -> Vuo:
    """Vaiheet riippuvuuksineen. Kaikki tulosteet menevät ajohakemistoon,
    joten saman vuon voi ajaa rinnakkain eri parametreilla."""
    rtl, tcl, tb = juuri / "rtl", juuri / "tcl", juuri / "tb"
    syn = ajohak / "synteesi"
    vuo = Vuo(ajohak, versiot=lambda v: versio(v.komento[0]))
    vuo.lisaa(Vaihe(
        "lint",
        ("verilator", "--lint-only", "-Wall", f"-GLEVEYS={leveys}",
         str(rtl / "laskuri.sv")),
        syotteet=(rtl / "laskuri.sv",), tulosteet=()))
    vuo.lisaa(Vaihe(
        "synteesi", ("yosys", "-q", "-c", str(tcl / "synteesi.tcl")),
        syotteet=(rtl / "laskuri.sv", tcl / "synteesi.tcl"),
        tulosteet=(syn / f"stat_{leveys}.json",
                   syn / f"laskuri_{leveys}.blif"),
        riippuu=("lint",),
        ymparisto=(("LEVEYDET", str(leveys)),
                   ("RTL", str(rtl / "laskuri.sv")), ("TULOS", str(syn)))))
    # @loppu kulku
    vuo.lisaa(Vaihe(
        "sta",
        (tclsh(), str(tcl / "opetus_sta.tcl"), "-source",
         str(tcl / "sta_kulku.tcl"), "--",
         str(syn / f"laskuri_{leveys}.blif"), str(jakso),
         str(ajohak / "sta.txt")),
        syotteet=(syn / f"laskuri_{leveys}.blif", tcl / "opetus_sta.tcl",
                  tcl / "sta_kulku.tcl"),
        tulosteet=(ajohak / "sta.txt",), riippuu=("synteesi",)))
    vuo.lisaa(Vaihe(
        "kaannos",
        ("verilator", "--binary", "-Wall", "--top-module", "alu_tb",
         "-Mdir", str(ajohak / "obj"), "-o", "sim",
         str(rtl / "alu.sv"), str(tb / "alu_tb.sv")),
        syotteet=(rtl / "alu.sv", tb / "alu_tb.sv"),
        tulosteet=(ajohak / "obj" / "sim",)))
    vuo.lisaa(Vaihe(
        "sim", (str(ajohak / "obj" / "sim"), "+siemen=1"),
        syotteet=(ajohak / "obj" / "sim",),
        tulosteet=(ajohak / "lokit" / "sim.log",), riippuu=("kaannos",)))
    return vuo

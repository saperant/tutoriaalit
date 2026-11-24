"""Simulaattorit saman rajapinnan takana: vuo ei tiedä, kumpi ajetaan."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from vuo.ajo import Ajo, aja


# @alku rajapinta
class Simulaattori(Protocol):
    nimi: str

    def kaanna(self, lahteet: list[Path], ylin: str,
               maarittelyt: list[str], hak: Path) -> Ajo: ...

    def aja(self, hak: Path, plusargit: list[str],
            aikaraja: float = 60.0) -> Ajo: ...
# @loppu rajapinta


# @alku toteutukset
class Verilator:
    nimi = "verilator"

    def kaanna(self, lahteet: list[Path], ylin: str,
               maarittelyt: list[str], hak: Path) -> Ajo:
        return aja(["verilator", "--binary", "-Wall", "--top-module", ylin,
                    *(f"-D{m}" for m in maarittelyt), "-Mdir",
                    str(hak / "obj"), "-o", "sim", *map(str, lahteet)],
                   hak / "kaannos.log")

    def aja(self, hak: Path, plusargit: list[str],
            aikaraja: float = 60.0) -> Ajo:
        return aja([str(hak / "obj" / "sim"), *plusargit],
                   hak / "sim.log", aikaraja=aikaraja)


# @loppu toteutukset


class Icarus:
    nimi = "icarus"

    def kaanna(self, lahteet: list[Path], ylin: str,
               maarittelyt: list[str], hak: Path) -> Ajo:
        return aja(["iverilog", "-g2012", "-s", ylin,
                    *(f"-D{m}" for m in maarittelyt),
                    "-o", str(hak / "sim.vvp"), *map(str, lahteet)],
                   hak / "kaannos.log")

    def aja(self, hak: Path, plusargit: list[str],
            aikaraja: float = 60.0) -> Ajo:
        # -n: $stop ei jää odottamaan interaktiivista komentoa.
        return aja(["vvp", "-n", str(hak / "sim.vvp"), *plusargit],
                   hak / "sim.log", aikaraja=aikaraja)

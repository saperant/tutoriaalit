"""Lähdeluettelo yhdestä paikasta: sama kuvaus jokaiselle työkalulle."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


# @alku kohde
@dataclass(frozen=True)
class Kohde:
    """Yksi käännettävä kokonaisuus: ylin moduuli ja kaikki, mitä sen
    kääntämiseen tarvitaan."""

    nimi: str
    ylin: str
    lahteet: tuple[Path, ...]
    hakupolut: tuple[Path, ...] = ()
    makrot: tuple[str, ...] = ()
    parametrit: dict[str, int] = field(default_factory=dict)


def lue(polku: Path, juuri: Path) -> dict[str, Kohde]:
    """Lukee luettelon ja hylkää sen, jos tiedosto puuttuu tai on
    lueteltu kahdesti. Virhe löytyy ennen kuin yhtään työkalua ajetaan."""
    kohteet = {}
    for nimi, t in tomllib.loads(polku.read_text()).items():
        lahteet = tuple(juuri / s for s in t["lahteet"])
        puuttuu = [str(p.relative_to(juuri)) for p in lahteet
                   if not p.is_file()]
        if puuttuu:
            raise ValueError(f"{nimi}: puuttuu {', '.join(puuttuu)}")
        if len(set(lahteet)) != len(lahteet):
            raise ValueError(f"{nimi}: sama tiedosto kahdesti")
        kohteet[nimi] = Kohde(
            nimi, t["ylin"], lahteet,
            tuple(juuri / h for h in t.get("hakupolut", [])),
            tuple(t.get("makrot", [])), dict(t.get("parametrit", {})))
    return kohteet
# @loppu kohde


# @alku komennot
def verilator_lint(k: Kohde) -> list[str]:
    return ["verilator", "--lint-only", "-Wall", "--top-module", k.ylin,
            *(f"-D{m}" for m in k.makrot),
            *(f"-I{h}" for h in k.hakupolut),
            *(f"-G{n}={a}" for n, a in k.parametrit.items()),
            *map(str, k.lahteet)]


def icarus(k: Kohde, tulos: Path) -> list[str]:
    return ["iverilog", "-g2012", "-s", k.ylin,
            *(f"-D{m}" for m in k.makrot),
            *(f"-I{h}" for h in k.hakupolut),
            *(f"-P{k.ylin}.{n}={a}" for n, a in k.parametrit.items()),
            "-o", str(tulos), *map(str, k.lahteet)]


def yosys_luku(k: Kohde) -> list[str]:
    """Yosysin Tcl-komennot, joilla kohde luetaan synteesiin."""
    valitsimet = [*(f"-D{m}" for m in k.makrot),
                  *(f"-I{h}" for h in k.hakupolut)]
    rivit = [" ".join(["read_verilog", "-sv", *valitsimet,
                       *map(str, k.lahteet)])]
    rivit += [f"chparam -set {n} {a} {k.ylin}"
              for n, a in k.parametrit.items()]
    return rivit
# @loppu komennot

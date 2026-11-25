"""Pieni mutaatiotestaaja: yksi pieni muutos kerrallaan, testit perään.

Oikeat työkalut (mutmut, cosmic-ray, Javan PIT, JavaScriptin Stryker)
toimivat samalla periaatteella mutta nopeammin ja useammilla
operaattoreilla.
"""

from __future__ import annotations

import ast
import copy
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

# Pytestin liitännäisiä ei ladata: jokainen mutantti käynnistää uuden
# prosessin, joten käynnistysaika ratkaisee.
YMPARISTO = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")

# @alku operaattorit
VERTAILUT: dict[type[ast.cmpop], type[ast.cmpop]] = {
    ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt,
    ast.Eq: ast.NotEq, ast.NotEq: ast.Eq,
}
LASKUT: dict[type[ast.operator], type[ast.operator]] = {
    ast.Add: ast.Sub, ast.Sub: ast.Add,
    ast.Mult: ast.FloorDiv, ast.FloorDiv: ast.Mult,
}
LOGIIKKA: dict[type[ast.boolop], type[ast.boolop]] = {
    ast.And: ast.Or, ast.Or: ast.And,
}
# @loppu operaattorit


@dataclass(frozen=True)
class Mutantti:
    rivi: int
    kuvaus: str
    lahde: str


# @alku muuntaja
class Muuntaja(ast.NodeTransformer):
    """Tekee puuhun muutoksen numero `kohde` ja jättää muun ennalleen."""

    def __init__(self, kohde: int) -> None:
        self.kohde = kohde
        self.paikkoja = 0
        self.rivi = 0
        self.kuvaus = ""

    def _vaihda(self, vanha: ast.expr, uusi: ast.expr) -> ast.expr:
        vuorossa = self.paikkoja == self.kohde
        self.paikkoja += 1
        if not vuorossa:
            return vanha
        self.rivi = vanha.lineno
        self.kuvaus = f"{ast.unparse(vanha)}  ->  {ast.unparse(uusi)}"
        return ast.copy_location(uusi, vanha)

    def visit_Compare(self, node: ast.Compare) -> ast.expr:
        self.generic_visit(node)
        if type(node.ops[0]) not in VERTAILUT:
            return node
        uusi = copy.copy(node)
        uusi.ops = [VERTAILUT[type(node.ops[0])](), *node.ops[1:]]
        return self._vaihda(node, uusi)

    def visit_BinOp(self, node: ast.BinOp) -> ast.expr:
        self.generic_visit(node)
        if type(node.op) not in LASKUT:
            return node
        uusi = copy.copy(node)
        uusi.op = LASKUT[type(node.op)]()
        return self._vaihda(node, uusi)

    def visit_BoolOp(self, node: ast.BoolOp) -> ast.expr:
        self.generic_visit(node)
        uusi = copy.copy(node)
        uusi.op = LOGIIKKA[type(node.op)]()
        return self._vaihda(node, uusi)

    def visit_Constant(self, node: ast.Constant) -> ast.expr:
        if type(node.value) is not int:
            return node
        return self._vaihda(node, ast.Constant(node.value + 1))
# @loppu muuntaja


# @alku mutantit
def mutantit(lahde: str) -> list[Mutantti]:
    tulos: list[Mutantti] = []
    kohde = 0
    while True:
        muuntaja = Muuntaja(kohde)
        puu = muuntaja.visit(ast.parse(lahde))
        if kohde >= muuntaja.paikkoja:
            return tulos
        tulos.append(Mutantti(muuntaja.rivi, muuntaja.kuvaus,
                              ast.unparse(puu)))
        kohde += 1


def selviaa(mutantti: Mutantti, moduuli: Path, testit: Path) -> bool:
    """Ajaa testit mutanttia vasten; True, jos yksikään testi ei kaadu."""
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / moduuli.name).write_text(mutantti.lahde, "utf-8")
        shutil.copy(testit, tmp)
        ajo = subprocess.run(
            [sys.executable, "-m", "pytest", "-x", "-q", "-p",
             "no:cacheprovider", testit.name],
            cwd=tmp, env=YMPARISTO, capture_output=True, check=False)
    return ajo.returncode == 0
# @loppu mutantit


def aja(moduuli: Path, testit: Path) -> list[tuple[Mutantti, bool]]:
    kaikki = mutantit(moduuli.read_text("utf-8"))
    with ThreadPoolExecutor(max_workers=4) as pooli:
        hengissa = list(pooli.map(
            lambda m: selviaa(m, moduuli, testit), kaikki))
    return list(zip(kaikki, hengissa, strict=True))

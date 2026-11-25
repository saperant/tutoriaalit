"""Vuon riippuvuusverkko Graphvizin DOT-kielellä.

Kuva tuotetaan samasta kuvauksesta kuin ajo: vaiheista, niiden
syötteistä ja tulosteista. Kun vuo muuttuu, kuva muuttuu mukana.
"""

from __future__ import annotations

from pathlib import Path

from vuo.vaiheet import Vuo

# Vaiheen tila kuvassa: täyttöväri ja reunan tyyli.
TYYLIT = {
    "ajettu": 'style="filled,bold", fillcolor="#f4c7a8"',
    "ajan tasalla": 'style=filled, fillcolor="#e6e6e6"',
    "ohitettu": 'style="filled,dashed", fillcolor=white',
    "epäonnistui": 'style="filled,bold", fillcolor="#e8a0a0"',
}


# @alku dot
def dot(vuo: Vuo, juuri: Path, nimi: str = "vuo",
        tilat: dict[str, str] | None = None) -> str:
    """Vaiheet laatikoina ja tiedostot soikioina. Tiedoston nimi
    näytetään suhteessa projektin juureen tai ajohakemistoon."""

    def lyhyt(polku: Path) -> str:
        for kanta in (vuo.ajohak, juuri):
            if polku.is_relative_to(kanta):
                return str(polku.relative_to(kanta))
        return polku.name

    rivit = [f"digraph {nimi} {{", "  rankdir=LR;",
             '  node [fontsize=10];']
    tiedostot: set[str] = set()
    for vaihe in vuo.vaiheet.values():
        tyyli = TYYLIT.get((tilat or {}).get(vaihe.nimi, ""), "")
        lisa = f", {tyyli}" if tyyli else ""
        rivit.append(f'  "{vaihe.nimi}" [shape=box{lisa}];')
        for syote in vaihe.syotteet:
            tiedostot.add(lyhyt(syote))
            rivit.append(f'  "{lyhyt(syote)}" -> "{vaihe.nimi}";')
        for tuloste in vaihe.tulosteet:
            tiedostot.add(lyhyt(tuloste))
            rivit.append(f'  "{vaihe.nimi}" -> "{lyhyt(tuloste)}";')
        # Vaihe ilman tiedostoa välissä: riippuvuus näkyy katkoviivana.
        for edeltaja in vaihe.riippuu:
            yhteiset = (set(vuo.vaiheet[edeltaja].tulosteet)
                        & set(vaihe.syotteet))
            if not yhteiset:
                rivit.append(f'  "{edeltaja}" -> "{vaihe.nimi}" '
                             "[style=dashed];")
    rivit[3:3] = [f'  "{t}" [shape=ellipse, fontsize=9];'
                  for t in sorted(tiedostot)]
    rivit.append("}")
    return "\n".join(rivit)
# @loppu dot

#!/usr/bin/env python3
"""Tuottaa kirjan kaaviot esimerkkien testatuista tulosteista.

Käyttö:  python3 kaaviot/tee.py            kirjoittaa kaaviot/*.dot
         python3 kaaviot/tee.py --tarkista  vertaa tallennettuihin

Lähteet ovat esimerkit/*.odotettu-tiedostoja, joita testaaja vertaa
ohjelmien tulosteisiin. Kaavio näyttää siis saman verkon tai rakenteen,
jonka esimerkkiohjelma oikeasti laskee.
"""

import re
import sys
from pathlib import Path

JUURI = Path(__file__).resolve().parent.parent
ESIMERKIT = JUURI / "esimerkit"
KOROSTUS = "#D8EFEB"
HUOMIO = "#F6D6CF"
MOLEMMAT = "#E3D9EE"
PUNAINEN = "#B04848"


def lue(nimi: str) -> str:
    return (ESIMERKIT / nimi).read_text("utf-8")


def rivi(nimi: str, alku: str) -> str:
    return next(r for r in lue(nimi).splitlines() if r.startswith(alku))


# --- Maksimivirta ja minimileikkaus ------------------------------------

def virtaus() -> str:
    virrat = re.findall(r"([A-F])-([A-F]) (\d+)/(\d+)",
                        rivi("10-virtaus.odotettu", "virrat:"))
    lahde = rivi("10-virtaus.odotettu", "lähteen puoli:").split(":")[1].split()
    leikkaus = set(re.findall(r"([A-F])-([A-F])",
                              rivi("10-virtaus.odotettu", "minimileikkaus:")))
    solmut = sorted({x for u, v, _, _ in virrat for x in (u, v)})
    ulos = ["digraph {", "  rankdir=LR; nodesep=0.4; ranksep=0.6;",
            "  edge [fontsize=8];",
            "  node [shape=circle, width=0.4, fixedsize=true];",
            '  subgraph cluster_S { label="S"; color="#D9E0E3"; '
            + " ".join(f"{x};" for x in solmut if x in lahde) + " }",
            '  subgraph cluster_T { label="T"; color="#D9E0E3"; '
            + " ".join(f"{x};" for x in solmut if x not in lahde) + " }"]
    for u, v, f, c in virrat:
        tyyli = ""
        if (u, v) in leikkaus:
            assert f == c, (u, v)           # leikkauksen kaari on täynnä
            tyyli = f', color="{PUNAINEN}", penwidth=1.6'
        elif u not in lahde and v in lahde:
            assert f == "0", (u, v)         # takaisin S:ään: tyhjä
            tyyli = ", style=dashed"
        ulos.append(f'  {u} -> {v} [label="{f}/{c}"{tyyli}];')
    ulos.append("}")
    return "\n".join(ulos) + "\n"


# --- 3-SAT riippumattomaksi joukoksi -----------------------------------

def reduktio() -> str:
    kaava = [k.split() for k in re.findall(
        r"\(([-\d ]+)\)", rivi("13-reduktio.odotettu", "kaava:"))]
    ristiriidat = re.findall(r"(\d+)-(\d+)",
                             rivi("13-reduktio.odotettu", "ristiriitakaaret:"))
    joukko = set(rivi("13-reduktio.odotettu",
                      "riippumaton joukko:").split(":")[1].split())
    ulos = ["graph {", "  nodesep=0.35; ranksep=0.5;",
            "  node [shape=circle, width=0.42, fixedsize=true, fontsize=10];"]
    for i, lauseke in enumerate(kaava):
        ulos.append(f"  subgraph cluster_{i} {{")
        ulos.append(f'    label="lauseke {i + 1}"; fontsize=9; color=white;')
        for j, lit in enumerate(lauseke):
            u = 3 * i + j
            nimi = ("¬" if lit.startswith("-") else "") + "x" + lit.lstrip("-")
            vari = (f', style=filled, fillcolor="{KOROSTUS}", penwidth=1.8'
                    if str(u) in joukko else "")
            ulos.append(f'    n{u} [label="{nimi}"{vari}];')
        a = 3 * i
        ulos.append(f"    n{a} -- n{a + 1}; n{a + 1} -- n{a + 2}; "
                    f"n{a} -- n{a + 2};")
        ulos.append("  }")
    for u, v in ristiriidat:
        ulos.append(f'  n{u} -- n{v} [style=dashed, color="{PUNAINEN}", '
                    "constraint=false];")
    ulos.append("}")
    return "\n".join(ulos) + "\n"


# --- Fenwick-puu -------------------------------------------------------

def fenwick() -> str:
    valit = {int(i): (int(a), int(b)) for i, a, b in re.findall(
        r"(\d+):\((\d+),(\d+)\]", rivi("07-fenwick.odotettu", "solmujen välit:"))}
    kysely = {int(x) for x in rivi("07-fenwick.odotettu",
                                   "summa(13)").split(":")[1].split()}
    paivitys = {int(x) for x in rivi("07-fenwick.odotettu",
                                     "lisaa(4, d)").split(":")[1].split()}
    n = max(valit)
    osat = ['<table border="0" cellborder="1" cellspacing="0" '
            'cellpadding="3">']
    pituus = n
    while pituus >= 1:                      # rivi kutakin välin pituutta kohti
        osat.append("<tr>")
        sarake = 1
        for i in sorted(valit):
            a, b = valit[i]
            if b - a != pituus:
                continue
            if a + 1 > sarake:
                osat.append(f'<td border="0" colspan="{a + 1 - sarake}"></td>')
            vari = (MOLEMMAT if i in kysely and i in paivitys
                    else KOROSTUS if i in kysely
                    else HUOMIO if i in paivitys else "white")
            osat.append(f'<td colspan="{pituus}" bgcolor="{vari}">{i}</td>')
            sarake = b + 1
        if sarake <= n:
            osat.append(f'<td border="0" colspan="{n + 1 - sarake}"></td>')
        osat.append("</tr>")
        pituus //= 2
    osat.append("<tr>")
    for i in range(1, n + 1):
        osat.append(f'<td border="0" width="20"><font point-size="8">{i}'
                    "</font></td>")
    osat.append("</tr></table>")
    return ("digraph {\n  t [shape=plain, style=solid, "
            f'label=<{"".join(osat)}>];\n}}\n')


KAAVIOT = {
    "virtaus-leikkaus.dot": virtaus,
    "reduktio-verkko.dot": reduktio,
    "fenwick-valit.dot": fenwick,
}


def main() -> int:
    tarkista = "--tarkista" in sys.argv[1:]
    virheita = 0
    for nimi, tee in KAAVIOT.items():
        polku = JUURI / "kaaviot" / nimi
        sisalto = tee()
        if tarkista:
            if not polku.exists() or polku.read_text("utf-8") != sisalto:
                print(f"VIRHE: {polku.relative_to(JUURI)} ei vastaa "
                      "esimerkkien tulosteita (aja python3 kaaviot/tee.py)")
                virheita += 1
        else:
            polku.write_text(sisalto, "utf-8")
    if tarkista and not virheita:
        print(f"OK: {len(KAAVIOT)} kaaviota vastaa esimerkkien tulosteita")
    return 1 if virheita else 0


if __name__ == "__main__":
    sys.exit(main())

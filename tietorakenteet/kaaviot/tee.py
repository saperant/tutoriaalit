#!/usr/bin/env python3
"""Tuottaa kirjan kaaviot esimerkkien testatuista tulosteista.

Käyttö:  python3 kaaviot/tee.py            kirjoittaa kaaviot/*.dot
         python3 kaaviot/tee.py --tarkista  vertaa tallennettuihin

Lähteet ovat esimerkit/*.odotettu-tiedostoja, joita testaaja vertaa
ohjelmien tulosteisiin. Kaavio näyttää siis saman taulukon, puun tai
graafin, jonka esimerkkiohjelma oikeasti rakentaa.
"""

import re
import sys
from pathlib import Path

JUURI = Path(__file__).resolve().parent.parent
ESIMERKIT = JUURI / "esimerkit"
KOROSTUS = "#D8EFEB"
HUOMIO = "#F6D6CF"
HARMAA = "#EEEEEE"


def rivit(nimi: str) -> list[str]:
    return (ESIMERKIT / nimi).read_text("utf-8").splitlines()


def rivi(nimi: str, alku: str) -> str:
    return next(r for r in rivit(nimi) if r.startswith(alku))


def taulukko(solut: list[str], varit: dict[int, str] | None = None,
             indeksit: bool = True, otsikko: str = "") -> str:
    """HTML-taulukko: yksi rivi soluja ja niiden alla paikkanumerot."""
    varit = varit or {}
    osat = ['<table border="0" cellborder="1" cellspacing="0" '
            'cellpadding="4">', "<tr>"]
    if otsikko:
        osat.append(f'<td border="0" align="right">{otsikko}  </td>')
    for i, solu in enumerate(solut):
        vari = f' bgcolor="{varit[i]}"' if i in varit else ""
        osat.append(f'<td port="p{i}" width="24"{vari}>{solu}</td>')
    osat.append("</tr>")
    if indeksit:
        osat.append("<tr>")
        if otsikko:
            osat.append('<td border="0"></td>')
        for i in range(len(solut)):
            osat.append(f'<td border="0"><font point-size="8">{i}</font>'
                        "</td>")
        osat.append("</tr>")
    osat.append("</table>")
    return "<" + "".join(osat) + ">"


# --- Rengaspuskuri kolmessa tilassa -----------------------------------

def rengas() -> str:
    ulos = ["digraph {", "  rankdir=TB; nodesep=0.3; ranksep=0.25;",
            "  node [shape=plain, style=solid]; edge [arrowsize=0.6];"]
    edellinen = None
    for n, tila in enumerate(("tyhjä", "kiertänyt", "täysi")):
        r = rivi("05-rengas.odotettu", tila + ":")
        m = re.match(r"\S+\s+\[(.*)\] luku (\d+), kirjoitus (\d+), "
                     r"täyttö (\d+)", r)
        assert m, r
        solut = [" " if s == "-" else "␣" if s == "_" else s
                 for s in m.group(1).split(" ")]
        luku, kirj, taytto = int(m.group(2)), int(m.group(3)), m.group(4)
        varit = {i: KOROSTUS for i, s in enumerate(m.group(1).split(" "))
                 if s != "-"}
        ulos.append(f"  t{n} [label={taulukko(solut, varit, otsikko=tila)}];")
        if luku == kirj:
            ulos.append(f'  i{n} [label="luku = kirjoitus (täyttö {taytto})"'
                        ", fontsize=9];")
            ulos.append(f"  i{n} -> t{n}:p{luku};")
        else:
            ulos.append(f'  l{n} [label="luku", fontsize=9]; '
                        f'k{n} [label="kirjoitus", fontsize=9];')
            ulos.append(f"  l{n} -> t{n}:p{luku}; k{n} -> t{n}:p{kirj};")
        if edellinen is not None:
            ulos.append(f"  t{edellinen} -> {'i' if luku == kirj else 'l'}{n}"
                        " [style=invis];")
        edellinen = n
    ulos.append("}")
    return "\n".join(ulos) + "\n"


# --- Pakan kasvatus ----------------------------------------------------

def pakka() -> str:
    ulos = ["digraph {", "  rankdir=TB; nodesep=0.3; ranksep=0.5;",
            "  node [shape=plain, style=solid]; edge [arrowsize=0.6];"]
    taulut = []
    for n, tila in enumerate(("täysi", "kasvatettu")):
        m = re.match(r"\S+\s+\[(.*)\] alku (\d+), määrä (\d+)",
                     rivi("05-pakka.odotettu", tila + ":"))
        assert m
        solut = m.group(1).split(" ")
        taulut.append((solut, int(m.group(2))))
        varit = {i: KOROSTUS for i, s in enumerate(solut) if s != "-"}
        nayta = [" " if s == "-" else s for s in solut]
        ulos.append(f"  t{n} [label={taulukko(nayta, varit, otsikko=tila)}];")
    vanha, alku = taulut[0]
    # Ensimmäinen ja viimeinen looginen alkio: mistä minne ne kopioidaan.
    for looginen in (0, len(vanha) - 1):
        ulos.append(f"  t0:p{(alku + looginen) % len(vanha)}:s -> "
                    f"t1:p{looginen}:n;")
    ulos.append(f'  a [label="alku", fontsize=9]; a -> t0:p{alku}:n;')
    ulos.append("}")
    return "\n".join(ulos) + "\n"


# --- Avoin osoitteistus: kokeilujakso ja hautakivi --------------------

def jakso() -> str:
    m = re.match(r"avainten (\d+), (\d+) ja (\d+) kotipaikka on (\d+)",
                 rivit("07-avoin.odotettu")[0])
    assert m
    koti, kolmas = int(m.group(4)), m.group(3)
    ulos = ["digraph {", "  rankdir=TB; nodesep=0.3; ranksep=0.2;",
            "  node [shape=plain, style=solid]; edge [arrowsize=0.6];"]
    nimet = {"lisätty": "kolme lisätty", "hautakivi": "keskimmäinen poistettu",
             "tyhjäksi": "virhe: merkitty tyhjäksi"}
    edellinen = None
    for n, tila in enumerate(nimet):
        solut = rivi("07-avoin.odotettu", tila + ":").split(":")[1].split()
        varit: dict[int, str] = {}
        nayta = []
        for i, s in enumerate(solut):
            if s == "+":
                varit[i] = HARMAA
                nayta.append("†")
            elif s == "-":
                nayta.append(" ")
            else:
                varit[i] = KOROSTUS
                nayta.append(s)
        if tila == "tyhjäksi":
            varit[koti + 1] = HUOMIO
        ulos.append(f"  t{n} [label="
                    f"{taulukko(nayta, varit, otsikko=nimet[tila])}];")
        if edellinen is not None:
            ulos.append(f"  t{edellinen} -> t{n} [style=invis];")
        edellinen = n
    ulos.append(f'  h [label="haku {kolmas}: kotipaikka {koti}", fontsize=9];')
    ulos.append(f"  h -> t0:p{koti}:n;")
    ulos.append("}")
    return "\n".join(ulos) + "\n"


# --- Hakupuut sulkulausekkeista ---------------------------------------

def jasenna(teksti: str) -> list[object]:
    sanat = teksti.replace("(", " ( ").replace(")", " ) ").split()
    pino: list[list[object]] = [[]]
    for s in sanat:
        if s == "(":
            pino.append([])
        elif s == ")":
            valmis = pino.pop()
            pino[-1].append(valmis)
        else:
            pino[-1].append(s)
    return pino[0][0]  # type: ignore[return-value]


def puu_dot(puu: list[object], etuliite: str, korostus: dict[str, str],
            ulos: list[str]) -> None:
    laskuri = [0]

    def solmu(x: list[object]) -> str:
        nimi = f"{etuliite}{laskuri[0]}"
        laskuri[0] += 1
        if not x:                       # tyhjä alipuu: näkymätön paikka
            ulos.append(f"    {nimi} [shape=point, style=invis];")
            return nimi
        avain = str(x[0])
        vari = (f', style=filled, fillcolor="{korostus[avain]}"'
                if avain in korostus else "")
        ulos.append(f'    {nimi} [label="{avain}"{vari}];')
        lapset = [lapsi for lapsi in x[1:] if isinstance(lapsi, list)]
        for lapsi in lapset:
            kohde = solmu(lapsi)
            tyyli = "" if lapsi else " [style=invis]"
            ulos.append(f"    {nimi} -> {kohde}{tyyli};")
        return nimi

    solmu(puu)


def puupari(lahteet: list[tuple[str, str, dict[str, str]]]) -> str:
    """Kaksi puuta rinnakkain: (tulosteen rivin alku, otsikko, korostus)."""
    ulos = ["digraph {", "  nodesep=0.25; ranksep=0.3;",
            "  node [shape=circle, width=0.4, fixedsize=true, fontsize=10];",
            "  edge [arrowsize=0.6];"]
    for n, (alku, otsikko, korostus) in enumerate(lahteet):
        r = rivi("08-hakupuu.odotettu", alku)
        puu = jasenna(r[r.index("("):])
        ulos.append(f"  subgraph cluster_{n} {{")
        ulos.append(f'    label="{otsikko}"; fontsize=10; color=white;')
        puu_dot(puu, f"p{n}_", korostus, ulos)
        ulos.append("  }")
    ulos.append("}")
    return "\n".join(ulos) + "\n"


def poisto() -> str:
    return puupari([
        ("puu ennen:", "ennen", {"30": HUOMIO, "35": KOROSTUS}),
        ("puu jälkeen:", "avain 30 poistettu", {"35": KOROSTUS}),
    ])


def epatasapaino() -> str:
    return puupari([
        ("4 2 6 1 3 5 7:", "lisätty järjestyksessä 4 2 6 1 3 5 7", {}),
        ("1..7 järjestyksessä:", "lisätty järjestyksessä 1 … 7", {}),
    ])


# --- Sama graafi kolmella tavalla -------------------------------------

def graafi() -> str:
    r = rivit("10-graafit.odotettu")
    kaaret = re.findall(r"(\d+)-(\d+)", r[0])
    n = int(re.search(r"(\d+) solmua", r[0]).group(1))  # type: ignore
    matriisi = [x.split() for x in r[2:2 + n]]
    alku = rivi("10-graafit.odotettu", "CSR alku:").split(":")[1].split()
    kohde = rivi("10-graafit.odotettu", "CSR kohde:").split(":")[1].split()

    ulos = ["digraph {", "  nodesep=0.3; ranksep=0.35; compound=true;",
            "  edge [arrowsize=0.6];",
            "  subgraph cluster_g {", '    label="graafi"; fontsize=10; '
            "color=white;",
            "    node [shape=circle, width=0.35, fixedsize=true, "
            "fontsize=10];"]
    for v in range(n):
        ulos.append(f'    v{v} [label="{v}"];')
    for a, b in kaaret:
        ulos.append(f"    v{a} -> v{b} [arrowhead=none];")
    ulos.append("  }")

    # Matriisi: rivi- ja sarakeotsikot, ykköset korostettuna.
    osat = ['<table border="0" cellborder="1" cellspacing="0" '
            'cellpadding="3">', '<tr><td border="0"></td>']
    osat += [f'<td border="0"><font point-size="8">{v}</font></td>'
             for v in range(n)]
    osat.append("</tr>")
    for u in range(n):
        osat.append(f'<tr><td border="0"><font point-size="8">{u}</font>'
                    "</td>")
        for v in range(n):
            vari = f' bgcolor="{KOROSTUS}"' if matriisi[u][v] == "1" else ""
            osat.append(f'<td width="18"{vari}>{matriisi[u][v]}</td>')
        osat.append("</tr>")
    osat.append("</table>")
    ulos.append("  subgraph cluster_m {")
    ulos.append('    label="vierekkäisyysmatriisi"; fontsize=10; color=white;')
    ulos.append(f'    m [shape=plain, style=solid, label=<{"".join(osat)}>];')
    ulos.append("  }")

    # Vierekkäisyyslistat CSR-taulukon järjestyksessä.
    ulos.append("  subgraph cluster_l {")
    ulos.append('    label="vierekkäisyyslistat"; fontsize=10; color=white;')
    lista = ['<table border="0" cellborder="0" cellspacing="2" '
             'cellpadding="2">']
    for v in range(n):
        naapurit = kohde[int(alku[v]):int(alku[v + 1])]
        lista.append(f'<tr><td border="1" width="18">{v}</td>'
                     f'<td align="left">→ {" → ".join(naapurit)}</td></tr>')
    lista.append("</table>")
    ulos.append(f'    l [shape=plain, style=solid, label=<{"".join(lista)}>];')
    ulos.append("  }")

    # CSR: alku-taulukon paikasta v nuoli solmun v naapurijakson alkuun.
    varit = {}
    for v in range(n):
        if v % 2 == 0:
            for i in range(int(alku[v]), int(alku[v + 1])):
                varit[i] = KOROSTUS
    ulos.append("  subgraph cluster_c {")
    ulos.append('    label="CSR"; fontsize=10; color=white;')
    ulos.append(f"    ca [shape=plain, style=solid, label="
                f"{taulukko(alku, otsikko='alku')}];")
    ulos.append(f"    ck [shape=plain, style=solid, label="
                f"{taulukko(kohde, varit, otsikko='kohde')}];")
    for v in range(n):
        ulos.append(f"    ca:p{v}:s -> ck:p{alku[v]}:n;")
    ulos.append("  }")
    # Asettelu: graafi, matriisi ja listat ylärivillä, CSR niiden alla.
    ulos.append("  m -> ca [style=invis]; l -> ca [style=invis];")
    ulos.append("}")
    return "\n".join(ulos) + "\n"


KAAVIOT = {
    "rengas-tilat.dot": rengas,
    "pakka-kasvatus.dot": pakka,
    "avoin-jakso.dot": jakso,
    "hakupuu-poisto.dot": poisto,
    "hakupuu-epatasapaino.dot": epatasapaino,
    "graafi-esitykset.dot": graafi,
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

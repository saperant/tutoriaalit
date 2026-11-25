#!/usr/bin/env python3
"""Tuottaa kirjan kaaviot esimerkkien testatuista tulosteista ja datasta.

Käyttö:  python3 kaaviot/tee.py            kirjoittaa kaaviot/*.dot
         python3 kaaviot/tee.py --tarkista  vertaa tallennettuihin

Lähteet ovat esimerkit/*.odotettu-tiedostoja, joita testaaja vertaa
ohjelmien tulosteisiin, sekä esimerkkiohjelmien omia syötetaulukoita.
Kaavio näyttää siis saman taulukon, puun tai graafin, jota esimerkki
käsittelee.
"""

import re
import sys
from pathlib import Path

JUURI = Path(__file__).resolve().parent.parent
ESIMERKIT = JUURI / "esimerkit"
KOROSTUS = "#D8EFEB"
HUOMIO = "#F6D6CF"
HARMAA = "#EEEEEE"
PUNAINEN = "#B04848"


def lue(nimi: str) -> str:
    return (ESIMERKIT / nimi).read_text("utf-8")


def rivi(nimi: str, alku: str) -> str:
    return next(r for r in lue(nimi).splitlines() if r.startswith(alku))


# --- Dynaamisen ohjelmoinnin taulukot ---------------------------------

def dp_taulukko(nimi: str) -> str:
    """Tulosteen taulukko HTML-taulukoksi; tähdellä merkityt korostetaan."""
    rivit = lue(nimi).splitlines()
    alku = next(i for i, r in enumerate(rivit) if r.startswith("taulukko "))
    sarakkeet = rivit[alku + 1].split()
    osat = ['<table border="0" cellborder="1" cellspacing="0" '
            'cellpadding="3">', '<tr><td border="0"></td>']
    for s in sarakkeet:
        merkki = "ε" if s == "-" else s
        osat.append(f'<td border="0"><b>{merkki}</b></td>')
    osat.append("</tr>")
    for r in rivit[alku + 2:alku + 2 + 64]:
        solut = r.split()
        if len(solut[0]) != 1:          # taulukon jälkeinen rivi
            break
        merkki = "ε" if solut[0] == "-" else solut[0]
        osat.append(f'<tr><td border="0"><b>{merkki}</b></td>')
        for s in solut[1:]:
            vari = f' bgcolor="{KOROSTUS}"' if s.startswith("*") else ""
            osat.append(f'<td width="20"{vari}>{s.lstrip("*")}</td>')
        osat.append("</tr>")
    osat.append("</table>")
    return ("digraph {\n  t [shape=plain, style=solid, "
            f'label=<{"".join(osat)}>];\n}}\n')


def lcs() -> str:
    return dp_taulukko("10-lcs.odotettu")


def editointi() -> str:
    return dp_taulukko("10-editointi.odotettu")


# --- Fibonaccin kutsupuut ---------------------------------------------

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


def fibonacci() -> str:
    # Sama argumentti saa saman sävyn, jolloin toistuvat alipuut näkyvät.
    savyt = {"3": HUOMIO, "2": KOROSTUS}
    ulos = ["digraph {", "  nodesep=0.15; ranksep=0.3;",
            "  node [shape=circle, width=0.32, fixedsize=true, fontsize=9];",
            "  edge [arrowsize=0.5];"]
    lahteet = [("kutsupuu F(5), suora:", "suora rekursio: 15 kutsua"),
               ("kutsupuu F(5), muisti:",
                "muistiinpano: 9 kutsua, katkoviiva = valmis arvo")]
    for n, (alku, otsikko) in enumerate(lahteet):
        r = rivi("09-fibonacci.odotettu", alku)
        puu = jasenna(r.split(":", 1)[1])
        laskuri = [0]
        ulos.append(f"  subgraph cluster_{n} {{")
        ulos.append(f'    label="{otsikko}"; fontsize=10; color=white;')

        def solmu(x: list[object], n: int = n) -> str:
            nimi = f"f{n}_{laskuri[0]}"
            laskuri[0] += 1
            arvo = str(x[0])
            muistista = arvo.endswith("*")
            arvo = arvo.rstrip("*")
            tyyli = '"filled,dashed"' if muistista else "filled"
            vari = savyt.get(arvo, "white")
            ulos.append(f'    {nimi} [label="{arvo}", style={tyyli}, '
                        f'fillcolor="{vari}"];')
            for lapsi in x[1:]:
                assert isinstance(lapsi, list)
                ulos.append(f"    {nimi} -> {solmu(lapsi)};")
            return nimi

        solmu(puu)
        kutsuja = laskuri[0]
        assert f" {kutsuja} kutsua" in otsikko, (otsikko, kutsuja)
        ulos.append("  }")
    ulos.append("}")
    return "\n".join(ulos) + "\n"


# --- Huffmanin puun yleisimmät merkit ---------------------------------

def huffman() -> str:
    koodit = re.findall(r"^'(.)'\s+(\d+)\s+([01]+)$", lue("08-huffman.odotettu"),
                        re.M)
    assert len(koodit) >= 5, koodit
    lehdet = {koodi: (merkki, maara) for merkki, maara, koodi in koodit}
    sisa: set[str] = {""}
    for koodi in lehdet:
        for i in range(1, len(koodi)):
            sisa.add(koodi[:i])
    ulos = ["digraph {", "  nodesep=0.12; ranksep=0.3;",
            "  node [fontsize=9]; edge [arrowsize=0.5, fontsize=8];"]
    for etuliite in sorted(sisa, key=lambda e: (len(e), e)):
        ulos.append(f'  n{etuliite or "j"} [shape=point, width=0.08];')
        for bitti in "01":
            lapsi = etuliite + bitti
            if lapsi in lehdet:
                merkki, maara = lehdet[lapsi]
                nimi = "väli" if merkki == " " else merkki
                ulos.append(f'  n{lapsi} [shape=box, style="rounded,filled", '
                            f'fillcolor="{KOROSTUS}", '
                            f'label="{nimi}\\n{maara} kpl\\n{lapsi}"];')
            elif lapsi not in sisa:
                # Alipuu, jonka merkit ovat harvinaisempia: ei piirretä.
                ulos.append(f'  n{lapsi} [shape=plaintext, style="", '
                            'label="…"];')
            ulos.append(f'  n{etuliite or "j"} -> n{lapsi} [label="{bitti}"];')
    ulos.append("}")
    return "\n".join(ulos) + "\n"


# --- Negatiivinen kaari -----------------------------------------------

def negatiivinen() -> str:
    lahde = lue("12-dijkstra.c")
    lohko = lahde[lahde.index("@alku negatiivinen"):
                  lahde.index("@loppu negatiivinen")]
    lohko = lohko[:lohko.index("dijkstra(")]        # ennen syklikaarta
    kaaret = re.findall(r"lisaa_kaari\(&g, (\d), (\d), (-?\d+)\)", lohko)
    assert len(kaaret) == 4, kaaret
    m = re.search(r"D:hen Dijkstra (\d+), Bellman-Ford (\d+)",
                  lue("12-dijkstra.odotettu"))
    assert m
    nimet = "ABCD"
    ulos = ["digraph {", "  rankdir=LR; nodesep=0.4; ranksep=0.6;",
            "  node [shape=circle, width=0.4, fixedsize=true, fontsize=10];",
            "  edge [fontsize=9];"]
    for u, v, paino in kaaret:
        tyyli = (f', color="{PUNAINEN}", fontcolor="{PUNAINEN}", penwidth=1.5'
                 if int(paino) < 0 else "")
        ulos.append(f'  {nimet[int(u)]} -> {nimet[int(v)]} '
                    f'[label="{paino.replace("-", "−")}"{tyyli}];')
    assert (m.group(1), m.group(2)) == ("3", "2")   # kuvatekstin luvut
    ulos.append("}")
    return "\n".join(ulos) + "\n"


# --- Pienin virittävä puu ---------------------------------------------

def virittava() -> str:
    lahde = lue("12-virittava.c")
    kylat = re.findall(r'"([^"]+)"', lahde[lahde.index("kyla[] = {"):
                                           lahde.index("Kaari reitit[]")])
    lohko = lahde[lahde.index("Kaari reitit[] = {"):lahde.index("Kaari puu[")]
    kaaret = re.findall(r"\{ (\d+), (\d+), (\d+) \}", lohko)
    assert len(kylat) == 6 and len(kaaret) == 10, (kylat, kaaret)
    valitut = set(rivi("12-virittava.odotettu", "kaivetaan:").split()[1:])
    # Kylien paikat kuvassa on valittu käsin niin, etteivät reitit risteä.
    paikat = {"Kangas": (0.0, 2.0), "Niemi": (4.2, 2.0), "Mäki": (2.2, 1.15),
              "Koski": (1.8, 0.1), "Aho": (0.0, -0.9), "Salo": (4.0, -0.9)}
    ulos = ["graph {", "  layout=neato;",
            "  node [shape=box, style=\"rounded,filled\", fontsize=10];",
            "  edge [fontsize=9];"]
    for kyla in kylat:
        x, y = paikat[kyla]
        ulos.append(f'  "{kyla}" [pos="{x},{y}!"];')
    for u, v, paino in kaaret:
        a, b = kylat[int(u)], kylat[int(v)]
        mukana = f"{a}-{b}" in valitut or f"{b}-{a}" in valitut
        tyyli = (f'color="{PUNAINEN}", penwidth=2.2' if mukana
                 else 'style=dashed')
        ulos.append(f'  "{a}" -- "{b}" [label="{paino}", {tyyli}];')
    ulos.append("}")
    assert sum("penwidth" in r for r in ulos) == len(valitut)
    return "\n".join(ulos) + "\n"


# --- Vahvasti yhtenäiset komponentit ----------------------------------

def komponentit() -> str:
    lahde = lue("11-komponentit.c")
    lohko = lahde[lahde.index("@alku palvelut"):lahde.index("Graafi g = ")]
    nimet = re.findall(r'"([a-zäö]+)"', lohko)
    kaaret = re.findall(r"\{ (\d), (\d) \}", lohko)
    tuloste = lue("11-komponentit.odotettu").splitlines()
    maara = int(tuloste[0].split()[0])
    ulos = ["digraph {", "  rankdir=LR; nodesep=0.3; ranksep=0.5;",
            "  node [shape=box, style=\"rounded,filled\", fontsize=10];"]
    for c in range(maara):
        jasenet = tuloste[1 + c].split(":")[1].split()
        ulos.append(f"  subgraph cluster_{c} {{")
        ulos.append('    style="rounded,dashed"; color=gray50; '
                    f'label="{c}"; fontsize=9;')
        for j in jasenet:
            vari = KOROSTUS if len(jasenet) > 1 else "white"
            ulos.append(f'    {j} [fillcolor="{vari}"];')
        ulos.append("  }")
    for u, v in kaaret:
        ulos.append(f"  {nimet[int(u)]} -> {nimet[int(v)]};")
    ulos.append("}")
    return "\n".join(ulos) + "\n"


KAAVIOT = {
    "lcs-taulukko.dot": lcs,
    "editointi-taulukko.dot": editointi,
    "fibonacci-kutsupuut.dot": fibonacci,
    "huffman-puu.dot": huffman,
    "negatiivinen-kaari.dot": negatiivinen,
    "virittava-puu.dot": virittava,
    "komponentit.dot": komponentit,
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
                      "esimerkkejä (aja python3 kaaviot/tee.py)")
                virheita += 1
        else:
            polku.write_text(sisalto, "utf-8")
    if tarkista and not virheita:
        print(f"OK: {len(KAAVIOT)} kaaviota vastaa esimerkkejä")
    return 1 if virheita else 0


if __name__ == "__main__":
    sys.exit(main())

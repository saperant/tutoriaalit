#!/usr/bin/env python3
"""Tuottaa kirjan kaaviot Kide-kääntäjän testatuista välitulosteista.

Käyttö:  python3 kaaviot/tee.py            kirjoittaa kaaviot/*.dot
         python3 kaaviot/tee.py --tarkista  vertaa tallennettuihin

Lähteet ovat esimerkit/naytteet/-hakemiston tulosteita, jotka
testaa.sh vertaa kääntäjän tulosteeseen. Kaavio on siis sama puu tai
graafi, jonka kääntäjä oikeasti rakentaa.
"""

import sys
from pathlib import Path

JUURI = Path(__file__).resolve().parent.parent
NAYTTEET = JUURI / "esimerkit" / "naytteet"


def lainaa(teksti: str) -> str:
    return teksti.replace("\\", "\\\\").replace('"', '\\"')


# --- Syntaksipuu S-lausekkeesta ---------------------------------------

def jasenna(teksti: str) -> list[object]:
    """Jäsentää S-lausekkeen sisäkkäisiksi listoiksi."""
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
    return pino[0]


def ast() -> str:
    puu = jasenna((NAYTTEET / "ast-presedenssi.txt").read_text("utf-8"))
    # Näytetään muuttujan b alustuslauseke: (var b LAUSEKE).
    funktio = puu[0]
    assert isinstance(funktio, list)
    var = next(x for x in funktio if isinstance(x, list) and x and x[0] == "var")
    rivit = ["digraph {", "  nodesep=0.15; ranksep=0.3;",
             "  node [shape=circle, width=0.4, fixedsize=true,",
             "        fontname=\"DejaVu Sans Mono\"];",
             "  edge [arrowhead=none];"]
    laskuri = [0]

    def solmu(x: object) -> str:
        nimi = f"n{laskuri[0]}"
        laskuri[0] += 1
        if isinstance(x, list):
            rivit.append(f'  {nimi} [label="{lainaa(str(x[0]))}"];')
            for lapsi in x[1:]:
                rivit.append(f"  {nimi} -> {solmu(lapsi)};")
        else:
            rivit.append(f'  {nimi} [label="{lainaa(str(x))}", '
                         'style="filled", fillcolor="#FFFFFF"];')
        return nimi

    solmu(var[2])
    rivit.append("}")
    return "\n".join(rivit) + "\n"


# --- Ohjausvuograafi välikielestä -------------------------------------

def cfg() -> str:
    lohkot: dict[str, list[str]] = {}
    nykyinen = ""
    for rivi in (NAYTTEET / "ir-summa.txt").read_text("utf-8").splitlines():
        if rivi.startswith("fn") or not rivi.strip():
            continue
        if not rivi.startswith(" "):
            nykyinen = rivi.split(":")[0]
            lohkot[nykyinen] = []
        else:
            lohkot[nykyinen].append(rivi.strip())
    rivit = ["digraph {", "  ranksep=0.3;",
             "  node [shape=box, fontname=\"DejaVu Sans Mono\",",
             "        fontsize=8];"]
    for nimi, kaskyt in lohkot.items():
        # Jokainen käsky omaksi merkkijonokseen (+ yhdistää), jotta rivit
        # pysyvät lyhyinä.
        osat = [f'"{lainaa(r)}\\l"' for r in
                [nimi + ":"] + ["  " + k for k in kaskyt]]
        rivit.append(f"  {nimi} [label=" + " +\n      ".join(osat) + "];")
    for nimi, kaskyt in lohkot.items():
        viimeinen = kaskyt[-1].replace(",", "").split()
        if viimeinen[0] == "jmp":
            rivit.append(f"  {nimi} -> {viimeinen[1]};")
        elif viimeinen[0] == "br":
            rivit.append(f'  {nimi} -> {viimeinen[2]} [label="tosi"];')
            rivit.append(f'  {nimi} -> {viimeinen[3]} [label="epätosi"];')
    rivit.append("}")
    return "\n".join(rivit) + "\n"


def dominanssi() -> str:
    rivit = ["digraph {", "  ranksep=0.3;",
             "  node [shape=circle, width=0.45, fixedsize=true];"]
    teksti = (NAYTTEET / "dominanssi-summa.txt").read_text("utf-8")
    for rivi in teksti.splitlines()[1:]:
        osat = rivi.split()
        lohko, idom = osat[0], osat[2]
        if idom != "-":
            rivit.append(f"  {idom} -> {lohko};")
        else:
            rivit.append(f"  {lohko};")
    rivit.append("}")
    return "\n".join(rivit) + "\n"


def elinvalit() -> str:
    """Elinvälit ajoituskaaviona: rivi kullekin virtuaalirekisterille."""
    import json
    teksti = (NAYTTEET / "valit-summa.txt").read_text("utf-8")
    rivit = []
    for rivi in teksti.splitlines()[1:]:
        nimi, valit, paikka = rivi.split("[")[0].strip(), \
            rivi.split("[")[1].split("]")[0], rivi.split("]")[1].strip()
        alku, loppu = (int(x) for x in valit.split(","))
        rivit.append((nimi, alku, loppu, paikka))
    pituus = max(r[2] for r in rivit) + 1
    signaalit = []
    for nimi, alku, loppu, paikka in rivit:
        aalto = ("z" + "." * (alku - 1) if alku else "") + "=" + \
            "." * (loppu - alku) + ("z" if loppu + 1 < pituus else "")
        aalto += "." * (pituus - len(aalto))
        signaalit.append({"name": nimi, "wave": aalto, "data": [paikka]})
    return json.dumps({"signal": signaalit, "config": {"hscale": 0.45}},
                      indent=1) + "\n"


KAAVIOT = {"ast-presedenssi.dot": ast, "cfg-summa.dot": cfg,
           "dominanssi-summa.dot": dominanssi,
           "valit-summa.json": elinvalit}


def main() -> None:
    tarkista = "--tarkista" in sys.argv
    virheita = 0
    for nimi, tee in KAAVIOT.items():
        polku = JUURI / "kaaviot" / nimi
        uusi = tee()
        if not tarkista:
            polku.write_text(uusi, "utf-8")
        elif not polku.exists() or polku.read_text("utf-8") != uusi:
            print(f"VIRHE: kaaviot/{nimi} ei vastaa kääntäjän tulostetta "
                  "(aja python3 kaaviot/tee.py)")
            virheita += 1
    if tarkista and not virheita:
        print(f"OK: {len(KAAVIOT)} kaaviota vastaa kääntäjän tulosteita")
    sys.exit(1 if virheita else 0)


if __name__ == "__main__":
    main()

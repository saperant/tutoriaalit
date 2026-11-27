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

def lue_lohkot(nayte: str) -> dict[str, list[str]]:
    """Välikielitulosteen lohkot: nimi -> käskyt (ilman kommentteja)."""
    lohkot: dict[str, list[str]] = {}
    nykyinen = ""
    for rivi in (NAYTTEET / nayte).read_text("utf-8").splitlines():
        if rivi.startswith("fn") or not rivi.strip():
            continue
        if not rivi.startswith(" "):
            nykyinen = rivi.split(":")[0]
            lohkot[nykyinen] = []
        else:
            lohkot[nykyinen].append(rivi.strip())
    return lohkot


def cfg_rivit(lohkot: dict[str, list[str]], etuliite: str = "",
              sisennys: str = "  ", kaskyn_sisennys: str = "  ") -> list[str]:
    """Lohkot solmuiksi ja päättävät käskyt kaariksi."""
    rivit = []
    for nimi, kaskyt in lohkot.items():
        # Jokainen käsky omaksi merkkijonokseen (+ yhdistää), jotta rivit
        # pysyvät lyhyinä.
        osat = [f'"{lainaa(r)}\\l"' for r in
                [nimi + ":"] + [kaskyn_sisennys + k for k in kaskyt]]
        rivit.append(f"{sisennys}{etuliite}{nimi} [label="
                     + f" +\n{sisennys}    ".join(osat) + "];")
    for nimi, kaskyt in lohkot.items():
        viimeinen = kaskyt[-1].replace(",", "").split()
        mista = f"{sisennys}{etuliite}{nimi} -> {etuliite}"
        if viimeinen[0] == "jmp":
            rivit.append(f"{mista}{viimeinen[1]};")
        elif viimeinen[0] == "br":
            rivit.append(f'{mista}{viimeinen[2]} [label="tosi"];')
            rivit.append(f'{mista}{viimeinen[3]} [label="epätosi"];')
    return rivit


def cfg() -> str:
    rivit = ["digraph {", "  ranksep=0.3;",
             "  node [shape=box, fontname=\"DejaVu Sans Mono\",",
             "        fontsize=8];"]
    rivit += cfg_rivit(lue_lohkot("ir-summa.txt"))
    rivit.append("}")
    return "\n".join(rivit) + "\n"


def cfg_laske() -> str:
    """Funktion laske ohjausvuograafi ennen SSA-optimointeja ja jälkeen."""
    rivit = ["digraph {", "  ranksep=0.22; nodesep=0.1; margin=0;",
             "  node [shape=box, fontname=\"DejaVu Sans Mono\",",
             "        fontsize=7.5, margin=\"0.09,0.05\"];",
             "  edge [fontsize=7];"]
    for etuliite, nayte, otsikko in (
            ("a", "ir-laske.txt", "-O1: paikalliset passit"),
            ("b", "ir-laske-O2.txt", "-O2: optimoitu SSA-muodossa")):
        rivit += [f"  subgraph cluster_{etuliite} {{",
                  f'    label="{otsikko}"; color="#D9E0E3"; margin=5;']
        rivit += cfg_rivit(lue_lohkot(nayte), etuliite, "    ", " ")
        rivit.append("  }")
    rivit.append("}")
    return "\n".join(rivit) + "\n"


def elavyys() -> str:
    """Ohjausvuograafi, jonka lohkoissa on elävyysanalyysin kiintopiste."""
    joukot: dict[str, tuple[str, str]] = {}
    for rivi in (NAYTTEET / "elavyys-summa.txt").read_text("utf-8").splitlines():
        osat = rivi.split()
        if osat and osat[0].startswith("L"):
            sisaan = rivi[rivi.index("sisään") + 7:rivi.index("ulos")].strip()
            ulos = rivi[rivi.index("ulos") + 5:].strip()
            joukot[osat[0]] = (sisaan, ulos)
    kaaret: list[tuple[str, str]] = []
    nykyinen = ""
    for rivi in (NAYTTEET / "ir-summa.txt").read_text("utf-8").splitlines():
        if rivi.startswith("fn") or not rivi.strip():
            continue
        if not rivi.startswith(" "):
            nykyinen = rivi.split(":")[0]
            continue
        sanat = rivi.replace(",", "").split()
        if sanat[0] == "jmp":
            kaaret.append((nykyinen, sanat[1]))
        elif sanat[0] == "br":
            kaaret += [(nykyinen, sanat[2]), (nykyinen, sanat[3])]
    assert set(joukot) == {a for a, _ in kaaret} | {b for _, b in kaaret}
    rivit = ["digraph {", "  ranksep=0.3;",
             "  node [shape=record, fontname=\"DejaVu Sans Mono\",",
             "        fontsize=8];"]
    for nimi, (sisaan, ulos) in joukot.items():
        s = lainaa(sisaan).replace("{", "\\{").replace("}", "\\}")
        u = lainaa(ulos).replace("{", "\\{").replace("}", "\\}")
        rivit.append(f'  {nimi} [label="{{sisään {s}|{nimi}|ulos {u}}}"];')
    for a, b in kaaret:
        rivit.append(f"  {a} -> {b};")
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
           "cfg-laske.dot": cfg_laske,
           "elavyys-summa.dot": elavyys,
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

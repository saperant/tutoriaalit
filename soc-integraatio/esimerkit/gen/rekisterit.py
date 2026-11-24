"""Rekisterigeneraattori: JSON-kuvaus → SystemVerilog, C ja Markdown.

Käyttö:
    python3 rekisterit.py gpio.json kohdehakemisto

Yksi kuvaus tuottaa kolme tiedostoa, jotka pysyvät siksi aina
yhtäpitävinä: APB-orjana toimivan rekisterilohkon (<nimi>_regs.sv),
ohjelmiston otsakkeen (<nimi>_regs.h) ja dokumentaation (<nimi>_regs.md).

Rekisterityypit:
    rw     ohjelmisto kirjoittaa ja lukee, laitteisto lukee (q)
    ro     laitteisto antaa arvon (d), ohjelmisto lukee
    wo     ohjelmiston kirjoitus antaa laitteistolle arvon ja pulssin
    w1c    laitteisto asettaa bittejä (set), ohjelmisto nollaa
           kirjoittamalla ykkösen (write 1 to clear)
    vakio  kiinteä arvo, esim. tunniste
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

TYYPIT = ("rw", "ro", "wo", "w1c", "vakio")
OTSAKE = "Generoitu tiedostosta {lahde} (gen/rekisterit.py). Älä muokkaa."


@dataclass(frozen=True)
class Rekisteri:
    nimi: str
    siirto: int
    leveys: int
    tyyppi: str
    nollaus: int
    kuvaus: str


@dataclass(frozen=True)
class Lohko:
    nimi: str
    kuvaus: str
    rekisterit: tuple[Rekisteri, ...]


# @alku lue
def lue(polku: Path) -> Lohko:
    """Lukee ja tarkistaa kuvauksen. Virheet kerrotaan heti."""
    data = json.loads(polku.read_text("utf-8"))
    rekisterit = []
    for r in data["rekisterit"]:
        rek = Rekisteri(r["nimi"], r["siirto"], r["leveys"], r["tyyppi"],
                        r.get("nollaus", 0), r["kuvaus"])
        if rek.tyyppi not in TYYPIT:
            raise ValueError(f"{rek.nimi}: tuntematon tyyppi {rek.tyyppi}")
        if rek.siirto % 4 or not 0 <= rek.siirto < 0x1000:
            raise ValueError(f"{rek.nimi}: siirto {rek.siirto:#x}")
        if not 1 <= rek.leveys <= 32 or rek.nollaus >= 1 << rek.leveys:
            raise ValueError(f"{rek.nimi}: leveys tai nollausarvo")
        rekisterit.append(rek)
    siirrot = [r.siirto for r in rekisterit]
    if len(set(siirrot)) != len(siirrot):
        raise ValueError("päällekkäiset siirrot")
    rekisterit.sort(key=lambda r: r.siirto)
    return Lohko(data["nimi"], data["kuvaus"], tuple(rekisterit))
# @loppu lue


# @alku portit
def portit(r: Rekisteri) -> list[str]:
    n = r.nimi.lower()
    w = f"[{r.leveys - 1}:0] " if r.leveys > 1 else ""
    return {
        "rw": [f"output logic {w}{n}_q"],
        "ro": [f"input  logic {w}{n}_d"],
        "wo": [f"output logic {w}{n}_q", f"output logic {n}_we"],
        "w1c": [f"input  logic {w}{n}_set", f"output logic {w}{n}_q"],
        "vakio": [],
    }[r.tyyppi]
# @loppu portit


def sv(lohko: Lohko, lahde: str) -> str:
    kaikki = [p for r in lohko.rekisterit for p in portit(r)]
    rivit = [f"// {OTSAKE.format(lahde=lahde)}",
             f"// {lohko.kuvaus}",
             f"module {lohko.nimi}_regs",
             "  import vaylat::*;",
             "(",
             "  input  logic     kello,",
             "  input  logic     nollaus_n,",
             "  input  apb_m2s_t apb_m,",
             "  output apb_s2m_t apb_s" + ("," if kaikki else "")]
    rivit += [f"  {p}," for p in kaikki[:-1]]
    if kaikki:
        rivit.append(f"  {kaikki[-1]}")
    rivit += [
        ");",
        "",
        "  // Kirjoitus tapahtuu APB:n ACCESS-vaiheessa; PSTRB rajaa tavut.",
        "  logic        kirjoita;",
        "  logic [31:0] maski;",
        "  assign kirjoita = apb_m.psel && apb_m.penable && apb_m.pwrite;",
        "  assign maski = {{8{apb_m.pstrb[3]}}, {8{apb_m.pstrb[2]}},",
        "                  {8{apb_m.pstrb[1]}}, {8{apb_m.pstrb[0]}}};",
        "",
        "  function automatic logic [31:0] sovita(input logic [31:0] vanha,",
        "                                        input logic [31:0] uusi,",
        "                                        input logic [31:0] m);",
        "    return (vanha & ~m) | (uusi & m);",
        "  endfunction",
        "",
    ]
    for r in lohko.rekisterit:
        n, w = r.nimi.lower(), r.leveys
        osuma = f"apb_m.paddr == 12'h{r.siirto:03X}"
        nollaus = f"{w}'h{r.nollaus:X}"
        alku = "  always_ff @(posedge kello or negedge nollaus_n)"
        if r.tyyppi == "rw":
            rivit += [alku,
                      f"    if (!nollaus_n) {n}_q <= {nollaus};",
                      f"    else if (kirjoita && {osuma})",
                      (f"      {n}_q <= {w}'(sovita(32'({n}_q), "
                       "apb_m.pwdata, maski));"),
                      ""]
        elif r.tyyppi == "wo":
            rivit += [f"  assign {n}_we = kirjoita && {osuma};",
                      f"  assign {n}_q  = apb_m.pwdata[{w - 1}:0];",
                      ""]
        elif r.tyyppi == "w1c":
            rivit += [alku,
                      f"    if (!nollaus_n) {n}_q <= {nollaus};",
                      f"    else if (kirjoita && {osuma})",
                      f"      {n}_q <= ({n}_q & ~{w}'(apb_m.pwdata & maski))",
                      f"              | {n}_set;",
                      f"    else {n}_q <= {n}_q | {n}_set;",
                      ""]
    rivit += [
        "  // Luku. Tuntematon osoite tai kirjoitus vain luettavaan",
        "  // rekisteriin vastaa virheellä (PSLVERR).",
        "  always_comb begin",
        "    apb_s        = '0;",
        "    apb_s.pready = 1'b1;",
        "    case (apb_m.paddr)",
    ]
    for r in lohko.rekisterit:
        n = r.nimi.lower()
        arvo = {"rw": f"{n}_q", "ro": f"{n}_d", "wo": "'0",
                "w1c": f"{n}_q", "vakio": f"{r.leveys}'h{r.nollaus:X}"}
        virhe = "kirjoita" if r.tyyppi in ("ro", "vakio") else "1'b0"
        rivit += [f"      12'h{r.siirto:03X}: begin",
                  f"        apb_s.prdata  = 32'({arvo[r.tyyppi]});",
                  f"        apb_s.pslverr = {virhe};",
                  "      end"]
    rivit += [
        "      default: apb_s.pslverr = apb_m.psel && apb_m.penable;",
        "    endcase",
        "  end",
        "",
        "endmodule",
        "",
    ]
    return "\n".join(rivit)


def c(lohko: Lohko, lahde: str) -> str:
    iso = lohko.nimi.upper()
    rivit = [f"/* {OTSAKE.format(lahde=lahde)} */",
             f"/* {lohko.kuvaus} */",
             f"#ifndef {iso}_REGS_H",
             f"#define {iso}_REGS_H", "",
             "#include <stddef.h>",
             "#include <stdint.h>", "",
             "typedef struct {"]
    kohta, vara = 0, 0
    for r in lohko.rekisterit:
        if r.siirto > kohta:
            rivit.append(f"    uint32_t varattu{vara}"
                         f"[{(r.siirto - kohta) // 4}];")
            vara += 1
        laatu = "const " if r.tyyppi in ("ro", "vakio") else ""
        rivit.append(f"    volatile {laatu}uint32_t {r.nimi};"
                     f"  /* {r.siirto:#05x} {r.tyyppi} */")
        kohta = r.siirto + 4
    rivit += [f"}} {lohko.nimi}_regs_t;", ""]
    for r in lohko.rekisterit:
        rivit.append(f"_Static_assert(offsetof({lohko.nimi}_regs_t, "
                     f"{r.nimi}) == {r.siirto:#x}, \"{r.nimi}\");")
    rivit.append("")
    for r in lohko.rekisterit:
        rivit.append(f"#define {iso}_{r.nimi}_MASKI "
                     f"0x{(1 << r.leveys) - 1:X}u")
    rivit += ["", f"#endif /* {iso}_REGS_H */", ""]
    return "\n".join(rivit)


def md(lohko: Lohko, lahde: str) -> str:
    rivit = [f"<!-- {OTSAKE.format(lahde=lahde)} -->",
             f"# {lohko.nimi}", "", lohko.kuvaus, ""]
    for r in lohko.rekisterit:
        teksti = (f"Tyyppi {r.tyyppi}, {r.leveys} bittiä, "
                  f"nollausarvo 0x{r.nollaus:X}. {r.kuvaus}.")
        rivit += [f"## {r.nimi} (0x{r.siirto:03X})", "",
                  *textwrap.wrap(teksti, 72), ""]
    return "\n".join(rivit)


def main() -> int:
    jasennin = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    jasennin.add_argument("kuvaus", type=Path)
    jasennin.add_argument("kohde", type=Path)
    argumentit = jasennin.parse_args()
    try:
        lohko = lue(argumentit.kuvaus)
    except (KeyError, ValueError) as virhe:
        print(f"{argumentit.kuvaus}: {virhe}", file=sys.stderr)
        return 1
    lahde = argumentit.kuvaus.name
    kohde = argumentit.kohde
    kohde.mkdir(parents=True, exist_ok=True)
    (kohde / f"{lohko.nimi}_regs.sv").write_text(sv(lohko, lahde), "utf-8")
    (kohde / f"{lohko.nimi}_regs.h").write_text(c(lohko, lahde), "utf-8")
    (kohde / f"{lohko.nimi}_regs.md").write_text(md(lohko, lahde), "utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

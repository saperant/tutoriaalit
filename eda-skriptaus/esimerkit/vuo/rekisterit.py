"""Rekisterikuvauksesta tuotettu koodi: RTL, C-otsake, dokumentti, testi."""

from __future__ import annotations

import re
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

LAADUT = {"rw", "ro", "w1c"}
TUNNISTE = re.compile(r"^[A-Z][A-Z0-9_]*$")


# @alku malli
@dataclass(frozen=True)
class Kentta:
    nimi: str
    msb: int
    lsb: int
    paasy: str              # rw, ro tai w1c (nollataan kirjoittamalla 1)
    nollaus: int
    kuvaus: str

    @property
    def leveys(self) -> int:
        return self.msb - self.lsb + 1

    @property
    def maski(self) -> int:
        return ((1 << self.leveys) - 1) << self.lsb


@dataclass(frozen=True)
class Rekisteri:
    nimi: str
    osoite: int
    kuvaus: str
    kentat: tuple[Kentta, ...]


@dataclass(frozen=True)
class Lohko:
    nimi: str
    perusosoite: int
    leveys: int
    rekisterit: tuple[Rekisteri, ...]


def lue(polku: Path) -> Lohko:
    data = tomllib.loads(polku.read_text(encoding="utf-8"))
    rekisterit = tuple(
        Rekisteri(r["nimi"], r["osoite"], r["kuvaus"], tuple(
            Kentta(k["nimi"], k["bitit"][0], k["bitit"][1], k["paasy"],
                   k.get("nollaus", 0), k["kuvaus"])
            for k in r.get("kentta", [])))
        for r in data["rekisteri"])
    lohko = data["lohko"]
    return Lohko(lohko["nimi"], lohko["perusosoite"], lohko["leveys"],
                 rekisterit)
# @loppu malli


# @alku tarkista
def tarkista(lohko: Lohko) -> list[str]:
    """Kaikki kuvauksen virheet kerralla; tyhjä lista, kun kunnossa."""
    virheet = []
    tavuja = lohko.leveys // 8
    osoitteet: dict[int, str] = {}
    for r in lohko.rekisterit:
        if not TUNNISTE.match(r.nimi):
            virheet.append(f"{r.nimi}: nimen on oltava isoin kirjaimin")
        if r.osoite % tavuja:
            virheet.append(f"{r.nimi}: osoite {r.osoite:#x} ei ole "
                           f"{tavuja} tavun rajalla")
        if r.osoite in osoitteet:
            virheet.append(f"{r.nimi}: osoite {r.osoite:#x} on jo "
                           f"rekisterillä {osoitteet[r.osoite]}")
        osoitteet.setdefault(r.osoite, r.nimi)
        if not r.kentat:
            virheet.append(f"{r.nimi}: ei kenttiä")
        # @alku kentat
        varattu = 0
        for k in r.kentat:
            paikka = f"{r.nimi}.{k.nimi}"
            if not 0 <= k.lsb <= k.msb < lohko.leveys:
                virheet.append(f"{paikka}: bitit [{k.msb}:{k.lsb}] eivät "
                               f"mahdu {lohko.leveys} bittiin")
                continue
            if varattu & k.maski:
                virheet.append(f"{paikka}: menee päällekkäin toisen "
                               "kentän kanssa")
            varattu |= k.maski
            if k.paasy not in LAADUT:
                virheet.append(f"{paikka}: tuntematon pääsy '{k.paasy}'")
            if k.nollaus >> k.leveys:
                virheet.append(f"{paikka}: nollausarvo {k.nollaus} ei "
                               f"mahdu {k.leveys} bittiin")
        # @loppu kentat
    return virheet
# @loppu tarkista


def otsikko(kommentti: str) -> str:
    return (f"{kommentti} Tuotettu tiedostosta asetukset/rekisterit.toml"
            f" (vuo/rekisterit.py).\n{kommentti} Älä muokkaa käsin: "
            "muutokset tehdään kuvaukseen.\n")


# @alku c
def c_otsake(lohko: Lohko) -> str:
    etu = lohko.nimi.upper()
    rivit = [f"/*\n{otsikko(' *')} */",
             f"#ifndef {etu}_REGS_H", f"#define {etu}_REGS_H", "",
             f"#define {etu}_PERUSOSOITE 0x{lohko.perusosoite:08X}u"]
    for r in lohko.rekisterit:
        nimi = f"{etu}_{r.nimi}"
        rivit += ["", f"/* {r.nimi}: {r.kuvaus} */",
                  f"#define {nimi}_OFFSET 0x{r.osoite:02X}u"]
        for k in r.kentat:
            rivit += [f"#define {nimi}_{k.nimi}_SHIFT {k.lsb}u",
                      f"#define {nimi}_{k.nimi}_MASK 0x{k.maski:08X}u"]
    rivit += ["", f"#endif /* {etu}_REGS_H */", ""]
    return "\n".join(rivit)
# @loppu c


def sv_tyyppi(leveys: int) -> str:
    """Porttien tyyppi tasattuna samaan leveyteen."""
    return ("logic" + (f" [{leveys - 1}:0]" if leveys > 1 else "")).ljust(12)


def signaali(r: Rekisteri, k: Kentta) -> str:
    return f"{r.nimi}_{k.nimi}".lower()


def osa(k: Kentta) -> str:
    return f"[{k.msb}:{k.lsb}]" if k.leveys > 1 else f"[{k.lsb}]"


# @alku sv
def sv_lohko(lohko: Lohko) -> str:
    portit = ["  input  logic        clk,", "  input  logic        rst_n,",
              "  input  logic        kirjoita,",
              "  input  logic [7:0]  osoite,",
              "  /* verilator lint_off UNUSEDSIGNAL */",
              "  input  logic [31:0] wdata,   // kaikkia bittejä ei käytetä",
              "  /* verilator lint_on UNUSEDSIGNAL */"]
    nollaus, kirjoitus, luku = [], [], []
    for r in lohko.rekisterit:
        portit.append(f"  // {r.nimi}: {r.kuvaus}")
        valinta = f"kirjoita && osoite == 8'h{r.osoite:02X}"
        rw, w1c = [], []
        luku.append(f"      8'h{r.osoite:02X}: begin")
        for k in r.kentat:
            s, t = signaali(r, k), sv_tyyppi(k.leveys)
            luku.append(f"        rdata{osa(k)} = {s};")
            if k.paasy == "ro":
                portit.append(f"  input  {t} {s},")
                continue
            if k.paasy == "w1c":
                portit.append(f"  input  {t} {s}_aseta,")
                w1c += [f"      if ({s}_aseta) {s} <= 1'b1;",
                        f"      else if ({valinta} && wdata{osa(k)})",
                        f"        {s} <= 1'b0;"]
            else:
                rw.append(f"        {s} <= wdata{osa(k)};")
            portit.append(f"  output {t} {s},")
            nollaus.append(f"      {s} <= {k.leveys}'h{k.nollaus:X};")
        luku.append("      end")
        if rw:
            kirjoitus += [f"      if ({valinta}) begin", *rw,
                          "      end"]
        kirjoitus += w1c
    portit.append("  output logic [31:0] rdata")
    return "\n".join([
        otsikko("//") + f"module {lohko.nimi}_regs (", *portit, ");",
        "  always_ff @(posedge clk or negedge rst_n) begin",
        "    if (!rst_n) begin", *nollaus,
        "    end else begin", *kirjoitus, "    end", "  end", "",
        "  always_comb begin", "    rdata = '0;", "    case (osoite)",
        *luku, "      default: ;", "    endcase", "  end",
        "endmodule", ""])
# @loppu sv


# @alku dok
def dokumentti(lohko: Lohko) -> str:
    rivit = [f"<!--\n{otsikko('  ')}-->", "",
             f"# Lohko {lohko.nimi}", "",
             f"Perusosoite 0x{lohko.perusosoite:08X}, rekisterit "
             f"{lohko.leveys}-bittisiä.", ""]
    for r in lohko.rekisterit:
        rivit += [f"## {r.nimi} (+0x{r.osoite:02X}): {r.kuvaus}", "",
                  "| Bitit | Kenttä | Pääsy | Nollaus | Kuvaus |",
                  "|-------|--------|-------|---------|--------|"]
        for k in r.kentat:
            bitit = f"{k.msb}:{k.lsb}" if k.leveys > 1 else str(k.lsb)
            rivit.append(f"| {bitit} | {k.nimi} | {k.paasy} | "
                         f"0x{k.nollaus:X} | {k.kuvaus} |")
        rivit.append("")
    return "\n".join(rivit)
# @loppu dok


def kuvio(leveys: int) -> int:
    """Testin syöttämä arvo vain luku -kentille: 0101...-kuvio."""
    return int("01" * leveys, 2) & ((1 << leveys) - 1)


# @alku testi
def sv_testi(lohko: Lohko) -> str:
    """Testipenkki: nollausarvot, kirjoitus ja luku, vain luku -kentät
    ja w1c-kenttien asetus ja nollaus väylän kautta."""
    nimi = f"{lohko.nimi}_regs"
    esittely, ajo = [], []
    nollaus_ajo, kirjoitus_ajo, w1c_ajo = [], [], []
    for r in lohko.rekisterit:
        o = f"8'h{r.osoite:02X}"
        maski = sum(k.maski for k in r.kentat)
        alku = kirjoitettu = 0
        for k in r.kentat:
            s, t = signaali(r, k), sv_tyyppi(k.leveys)
            if k.paasy == "ro":
                arvo = kuvio(k.leveys)
                esittely.append(f"  {t} {s} = {k.leveys}'h{arvo:X};")
                alku |= arvo << k.lsb
                kirjoitettu |= arvo << k.lsb
                continue
            esittely.append(f"  {t} {s};")
            nollaus_ajo.append(
                f"    tarkista({s} == {k.leveys}'h{k.nollaus:X}, "
                f"\"{r.nimi}.{k.nimi} lähtö nollauksessa\");")
            alku |= k.nollaus << k.lsb
            if k.paasy == "rw":
                kirjoitettu |= k.maski
            else:
                esittely.append(f"  {t} {s}_aseta = 1'b0;")
                w1c_ajo += [
                    f"    @(negedge clk) {s}_aseta = 1'b1;",
                    f"    @(negedge clk) {s}_aseta = 1'b0;",
                    f"    lue({o}, 32'h{k.maski:08X}, 32'h{k.maski:08X},"
                    f" \"{r.nimi}.{k.nimi} asetettu\");",
                    f"    kirjoita_rek({o}, 32'h{k.maski:08X});",
                    f"    lue({o}, 32'h0, 32'h{k.maski:08X},"
                    f" \"{r.nimi}.{k.nimi} nollattu\");"]
        nollaus_ajo.append(f"    lue({o}, 32'h{alku:08X}, 32'h{maski:08X},"
                           f" \"{r.nimi} nollausarvo\");")
        kirjoitus_ajo += [
            f"    kirjoita_rek({o}, 32'hFFFFFFFF);",
            f"    lue({o}, 32'h{kirjoitettu:08X}, 32'h{maski:08X},"
            f" \"{r.nimi} kirjoitus\");"]
    ajo = nollaus_ajo + kirjoitus_ajo + w1c_ajo
    return "\n".join([
        otsikko("//") + f"module {nimi}_tb;",
        "  logic clk = 1'b0, rst_n = 1'b0, kirjoita = 1'b0;",
        "  logic [7:0] osoite = '0;",
        "  logic [31:0] wdata = '0, rdata;", *esittely,
        "  int virheet = 0, tarkistuksia = 0;", "",
        f"  {nimi} dut (.*);", "  initial forever #5 clk = ~clk;", "",
        "  task automatic tarkista(input logic ehto, input string mita);",
        "    tarkistuksia++;",
        "    if (!ehto) begin",
        "      virheet++;",
        "      $display(\"VIRHE %s\", mita);",
        "    end",
        "  endtask", "",
        "  task automatic lue(input logic [7:0] o, input logic [31:0] arvo,",
        "                     input logic [31:0] maski, input string mita);",
        "    @(negedge clk) osoite = o;",
        "    #1 tarkista((rdata & maski) == arvo, mita);",
        "  endtask", "",
        "  task automatic kirjoita_rek(input logic [7:0] o,",
        "                              input logic [31:0] d);",
        "    @(negedge clk) begin",
        "      osoite = o; wdata = d; kirjoita = 1'b1;",
        "    end",
        "    @(negedge clk) kirjoita = 1'b0;",
        "  endtask", "",
        "  initial begin",
        "    #12 rst_n = 1'b1;", *ajo,
        "    if (virheet == 0)",
        "      $display(\"REKISTERITESTI OK %0d tarkistusta\", "
        "tarkistuksia);",
        "    else $display(\"REKISTERITESTI EPÄONNISTUI %0d virhettä\", "
        "virheet);",
        "    $finish;", "  end", "endmodule", ""])
# @loppu testi


# @alku tuota
TUOTTEET: dict[str, Callable[[Lohko], str]] = {
    "{}_regs.sv": sv_lohko,
    "{}_regs_tb.sv": sv_testi,
    "{}_regs.h": c_otsake,
    "{}_regs.md": dokumentti,
}


def tuota(lohko: Lohko) -> dict[str, str]:
    """Tiedostonimi -> sisältö. Ei kirjoita mitään: kutsuja päättää,
    kirjoitetaanko vai verrataanko."""
    return {malli.format(lohko.nimi): f(lohko)
            for malli, f in TUOTTEET.items()}


def vertaa(lohko: Lohko, hakemisto: Path) -> list[str]:
    """Tuotetut tiedostot, jotka puuttuvat tai poikkeavat levyllä
    olevista: CI:n tarkistus, että kuvaus ja koodi ovat samassa tahdissa."""
    return [nimi for nimi, sisalto in tuota(lohko).items()
            if not (hakemisto / nimi).exists()
            or (hakemisto / nimi).read_text(encoding="utf-8") != sisalto]
# @loppu tuota

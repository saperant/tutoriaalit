"""Formaali tarkistus Yosysilla ja yosys-smtbmc:llä (luku 8).

Tekee saman kuin SymbiYosysin .sby-tiedosto (ks. formaali/fifo.sby),
mutta kahdella suoralla komennolla:

  1. yosys lukee lähteet makrolla FORMAL ja kirjoittaa mallin SMT2-
     muodossa (read_verilog -formal; prep; async2sync; write_smt2)
  2. yosys-smtbmc ajaa ratkaisijaa (z3) tilassa bmc, prove tai cover

Tuloste on lyhennetty ja deterministinen: aikaleimat, sisäiset
tunnisteet ja polut poistetaan. Jos ratkaisija tuottaa jäljen
(vastaesimerkin tai cover-jäljen), se tulostetaan taulukkona.

Käyttö:
  python3 tyokalut/formaali.py --top fifo --lahde rtl/fifo.sv \\
      --tila bmc --syvyys 10 [-D MAKRO] [--signaalit rst,push,pop]

Paluuarvo on 0, kun tila on PASSED, ja muuten 1.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

RAKENNUS = Path("rakennus/formaali")

# yosys-smtbmc:n viestit, jotka näytetään (muut ovat edistymistietoa).
NAYTETTAVAT = (
    "BMC failed!",
    "Assert failed",
    "Assumptions are unsatisfiable!",
    "Temporal induction failed!",
    "Temporal induction successful.",
    "Reached cover statement",
    "Unreached cover statement",
    "Status:",
)


# @alku vcd
def lue_vcd(polku: Path) -> list[dict[str, str]]:
    """Lukee yosys-smtbmc:n VCD-jäljen: yksi sanakirja askelta kohden."""
    nimet: dict[str, str] = {}  # tunniste -> signaalin nimi
    askeleet: list[dict[str, str]] = []
    kirjoitetut: list[int] = []  # montako arvoa kullakin askeleella
    alue: list[str] = []  # moduulihierarkia ilman ylintä moduulia
    for rivi in polku.read_text().splitlines():
        osat = rivi.split()
        if osat[:1] == ["$scope"]:
            alue.append(osat[2].replace("<", "[").replace(">", "]"))
        elif osat[:1] == ["$upscope"]:
            alue.pop()
        elif len(osat) >= 5 and osat[:2] == ["$var", "wire"]:
            nimet[osat[3]] = ".".join([*alue[1:], osat[4]])
        elif len(osat) == 2 and osat[0].startswith("b"):
            if osat[1] == "t":  # smt_step: uusi askel alkaa
                askeleet.append(dict(askeleet[-1]) if askeleet else {})
                kirjoitetut.append(0)
            elif osat[1] in nimet and askeleet:
                askeleet[-1][nimet[osat[1]]] = osat[0][1:]
                kirjoitetut[-1] += 1
    # Viimeinen askel sisältää vain kellon reunan: se jätetään pois.
    if len(askeleet) > 1 and kirjoitetut[-1] <= 1:
        askeleet.pop()
    return askeleet
    # @loppu vcd


def arvo(bitit: str, binaari: bool) -> str:
    """Muuttaa bittijonon luvuksi; x ja z näytetään sellaisinaan."""
    if binaari or "x" in bitit or "z" in bitit:
        return bitit if binaari or len(bitit) == 1 else "x"
    return str(int(bitit, 2))


def taulukko(askeleet: list[dict[str, str]], signaalit: list[str]) -> None:
    """Tulostaa jäljen. Nimen pääte :b näyttää arvon bitteinä."""
    nimet = [s.removesuffix(":b") for s in signaalit]
    leveys = [max(len(n), 3) for n in nimet]

    def sarakkeet(solut: list[str]) -> str:
        pari = zip(solut, leveys, strict=True)
        return " ".join(f"{c:>{w}}" for c, w in pari)

    print("  askel " + sarakkeet(nimet))
    for i, rivi in enumerate(askeleet):
        solut = [
            arvo(rivi.get(n, "x"), s.endswith(":b"))
            for n, s in zip(nimet, signaalit, strict=True)
        ]
        print(f"  {i:>5} " + sarakkeet(solut))


def siisti(rivi: str) -> str:
    """Poistaa aikaleiman ja sisäisen tunnisteen, jättää rivinumeron."""
    rivi = re.sub(r"^##\s+\d+:\d+:\d+\s+", "", rivi)
    rivi = re.sub(r" \(\$(assert|cover)\$[^)]*\)", "", rivi)
    # Yosys antaa alueen alku.sarake-loppu.sarake; lause päättyy loppuun.
    return re.sub(r"(\.sv:)\d+\.\d+-(\d+)\.\d+", r"\1\2", rivi)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--top", required=True)
    p.add_argument("--lahde", action="append", required=True)
    p.add_argument("--tila", choices=["bmc", "prove", "cover"], default="bmc")
    p.add_argument("--syvyys", type=int, default=10)
    p.add_argument("-D", dest="makrot", action="append", default=[])
    p.add_argument("--signaalit", default="")
    a = p.parse_args()

    nimi = "-".join([a.top, a.tila, *a.makrot]).lower()
    hakemisto = RAKENNUS / nimi
    hakemisto.mkdir(parents=True, exist_ok=True)
    for vanha in hakemisto.glob("*.vcd"):
        vanha.unlink()
    malli = hakemisto / "malli.smt2"

    # @alku yosys
    maaritteet = " ".join(f"-D{m}" for m in a.makrot)
    skripti = (
        f"read_verilog -sv -formal {maaritteet} {' '.join(a.lahde)}; "
        f"prep -top {a.top}; async2sync; dffunmap; "
        f"write_smt2 -wires {malli}"
    )
    subprocess.run(["yosys", "-q", "-p", skripti], check=True)
    # @loppu yosys

    # @alku smtbmc
    valinta = {"bmc": [], "prove": ["-i"], "cover": ["-c"]}[a.tila]
    jalki = str(hakemisto / "jalki%.vcd")  # % = cover-jäljen numero
    komento = ["yosys-smtbmc", "-s", "z3", *valinta, "-t", str(a.syvyys)]
    komento += ["--dump-vcd", jalki, str(malli)]
    ajo = subprocess.run(komento, capture_output=True, text=True, check=False)
    # @loppu smtbmc

    makrot = ", ".join(a.makrot) if a.makrot else "ei"
    print(f"{a.top}: tila {a.tila}, syvyys {a.syvyys}, makrot: {makrot}")
    viestit: dict[str, int] = {}
    for rivi in map(siisti, ajo.stdout.splitlines()):
        if rivi.startswith(NAYTETTAVAT):
            viestit[rivi] = viestit.get(rivi, 0) + 1
    tila = "?"
    for rivi, kerrat in viestit.items():
        # Silmukan (genvar) kopiot antavat saman viestin: näytetään kerran.
        print(rivi if kerrat == 1 else f"{rivi} ({kerrat} kertaa)")
        kohta = re.search(r"([\w/.-]+\.sv):(\d+)", rivi)
        if kohta and rivi.startswith("Assert failed"):
            lahde = Path(kohta[1]).read_text().splitlines()
            print("  > " + lahde[int(kohta[2]) - 1].strip())
        if rivi.startswith("Status:"):
            tila = rivi.split()[1]
    signaalit = [s for s in a.signaalit.split(",") if s]
    yksi = hakemisto / "jalki%.vcd"  # muu kuin cover: yksi jälki
    if yksi.exists():
        yksi.rename(hakemisto / "jalki.vcd")
    jaljet = sorted(hakemisto.glob("jalki*.vcd"))
    for polku in jaljet if signaalit else []:
        otsikko = "jälki" if len(jaljet) == 1 else f"jälki {polku.stem[5:]}"
        print(f"{otsikko}:")
        taulukko(lue_vcd(polku), signaalit)
    if tila == "?":
        print(ajo.stdout + ajo.stderr, file=sys.stderr)
    return 0 if tila == "PASSED" else 1


if __name__ == "__main__":
    sys.exit(main())

"""Rekisterikuvauksesta tuotettu koodi ja sen tarkistukset.

    python3 09-rekisterit.py             tarkistaa ja testaa
    python3 09-rekisterit.py --kirjoita  tuottaa hakemiston tuotettu/
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

from vuo.ajo import aja
from vuo.rekisterit import Lohko, lue, tarkista, tuota, vertaa

JUURI = Path(__file__).resolve().parent
TUOTETTU = JUURI / "tuotettu"


# @alku tarkistus
def kuvauksen_tarkistus() -> Lohko:
    rikki = lue(JUURI / "asetukset" / "rekisterit_rikki.toml")
    print("rekisterit_rikki.toml:")
    for virhe in tarkista(rikki):
        print(f"  {virhe}")
    lohko = lue(JUURI / "asetukset" / "rekisterit.toml")
    virheet = tarkista(lohko)
    print(f"rekisterit.toml: {len(virheet)} virhettä")
    return lohko
# @loppu tarkistus


# @alku testi
def aja_testi(lahde: Path, hak: Path, otsikko: str) -> None:
    """Tuotettu RTL lint-tarkistetaan ja tuotettu testipenkki ajetaan.
    Käännöstuotteet menevät hakemistoon hak, ei lähteiden viereen."""
    hak.mkdir(parents=True)
    for nimi in ("ajastin_regs.sv", "ajastin_regs_tb.sv"):
        shutil.copy(lahde / nimi, hak / nimi)
    lint = aja(["verilator", "--lint-only", "-Wall",
                str(hak / "ajastin_regs.sv")], hak / "lint.log")
    aja(["verilator", "--binary", "-Wall", "--top-module",
         "ajastin_regs_tb", "-Mdir", str(hak / "obj"), "-o", "sim",
         str(hak / "ajastin_regs.sv"), str(hak / "ajastin_regs_tb.sv")],
        hak / "kaannos.log")
    sim = aja([str(hak / "obj" / "sim")], hak / "sim.log")
    rivit = [r for r in sim.loki.read_text().splitlines()
             if r.startswith(("VIRHE", "REKISTERITESTI"))]
    print(f"{otsikko}: lint {'puhdas' if lint.onnistui else 'VAROITUKSIA'}")
    for rivi in rivit:
        print(f"  {rivi}")
# @loppu testi


def c_ajuri(tmp: Path) -> None:
    kaantaja = next((k for k in ("cc", "gcc", "gcc-14", "clang-20")
                     if shutil.which(k)), "cc")
    kaannos = aja([kaantaja, "-std=c11", "-Wall", "-Wextra", "-Werror",
                   "-I", str(TUOTETTU), "-o", str(tmp / "ajuri"),
                   str(JUURI / "c" / "ajuri.c")], tmp / "cc.log")
    print(f"c/ajuri.c: käännös {'onnistui' if kaannos.onnistui else 'EI'}")
    ajo = aja([str(tmp / "ajuri")], tmp / "ajuri.log")
    for rivi in ajo.loki.read_text().splitlines()[1:]:
        print(f"  {rivi}")


def main() -> None:
    jasennin = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    jasennin.add_argument("--kirjoita", action="store_true")
    argumentit = jasennin.parse_args()
    lohko = kuvauksen_tarkistus()
    # @alku tahdissa
    if argumentit.kirjoita:
        TUOTETTU.mkdir(exist_ok=True)
        for nimi, sisalto in tuota(lohko).items():
            (TUOTETTU / nimi).write_text(sisalto, encoding="utf-8")
    poikkeavat = vertaa(lohko, TUOTETTU)
    print("tuotettu/: " + ("ajan tasalla" if not poikkeavat else
                           "VANHENTUNUT: " + ", ".join(poikkeavat)))
    # @loppu tahdissa
    with tempfile.TemporaryDirectory() as tmp:
        hak = Path(tmp)
        aja_testi(TUOTETTU, hak / "testi", "tuotettu/")
        # @alku kasin
        # Joku "korjaa" tuotettua tiedostoa käsin: nollausarvo muuttuu.
        kopio = hak / "kasin"
        shutil.copytree(TUOTETTU, kopio)
        sv = kopio / "ajastin_regs.sv"
        sv.write_text(sv.read_text().replace("ctrl_jakaja <= 8'h1;",
                                             "ctrl_jakaja <= 8'h0;"))
        print("käsin muokattu kopio: poikkeaa " +
              ", ".join(vertaa(lohko, kopio)))
        aja_testi(kopio, hak / "testi2", "käsin muokattu kopio")
        # @loppu kasin
        c_ajuri(hak)


if __name__ == "__main__":
    main()

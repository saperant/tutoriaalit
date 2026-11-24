"""Lint-varoitukset luokiteltuina: vakavuus, sallitut ja laatuportti."""

from __future__ import annotations

import tempfile
from collections import Counter
from datetime import date
from pathlib import Path

from vuo.ajo import aja
from vuo.raportit import lue_verilator
from vuo.varoitukset import luokittele, lue_sallitut, vakavuus

JUURI = Path(__file__).resolve().parent
# Kiinteä päivä, jotta tulos ei muutu ajan kuluessa; vuossa date.today().
TANAAN = date(2026, 11, 24)


# @alku lint
def lint(tmp: Path) -> bool:
    ajo = aja(["verilator", "--lint-only", "-Wall", "-Wno-fatal",
               "rtl/ohjain.sv"], tmp / "lint.log", hakemisto=JUURI)
    # Järjestys tiedoston ja rivin mukaan: työkalun oma järjestys voi
    # vaihdella versiosta toiseen.
    varoitukset = sorted(lue_verilator(ajo.loki.read_text(), JUURI),
                         key=lambda v: (v.tiedosto, v.rivi, v.koodi))
    maarat = Counter(vakavuus(v) for v in varoitukset)
    print("vakavuus:", ", ".join(f"{k} {n}" for k, n in
                                 sorted(maarat.items())))
    tulos = luokittele(varoitukset, lue_sallitut(
        JUURI / "asetukset" / "sallitut.toml"), TANAAN)
    for otsikko, lista in (("uudet", tulos.uudet),
                           ("sallitut", tulos.sallitut),
                           ("vanhentuneet", tulos.vanhentuneet)):
        print(f"{otsikko}:")
        for v in lista:
            print(f"  {v.koodi:12} {v.tiedosto}:{v.rivi}")
    print("tarpeettomat sallinnat:")
    for s in tulos.tarpeettomat:
        print(f"  {s.koodi:12} {s.tiedosto} ({s.kuvio})")
    print(f"laatuportti: {'läpi' if tulos.lapi else 'HYLÄTTY'}")
    return tulos.lapi
# @loppu lint


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        lapi = lint(Path(tmp))
    # Vuossa hylkäys olisi paluuarvo 1; esimerkki näyttää sen tulosteena.
    print(f"paluuarvo vuossa: {0 if lapi else 1}")


if __name__ == "__main__":
    main()

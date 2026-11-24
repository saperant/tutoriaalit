"""Siirtymä omasta kuvausmuodosta SystemRDL:ään.

Taidossa EDA-työkaluketjujen automatisointi ajastimen rekisterit on
kuvattu omana TOML-muotonaan (vertailu/rekisterit.toml). Tämä ohjelma
muuntaa sen SystemRDL:ksi, kääntää tuloksen ja vertaa sitä käsin
kirjoitettuun kuvaukseen rdl/ajastin.rdl.
"""

from __future__ import annotations

import tempfile
import tomllib
from pathlib import Path
from typing import Any

from kuvaus.kaanna import kaanna
from kuvaus.malli import Rekisteri, rekisterit

VERTAILU = Path(__file__).resolve().parent / "vertailu"

# @alku muunnos
PAASY = {"rw": "sw = rw; hw = r;",
         "ro": "sw = r; hw = w;",
         "w1c": "sw = rw; hw = na; hwset; onwrite = woclr;"}


def muunna(kuvaus: dict[str, Any]) -> str:
    """Oman muodon kuvaus SystemRDL-tekstiksi."""
    lohko = kuvaus["lohko"]
    rivit = [f"addrmap {lohko['nimi']} {{",
             f"    default regwidth = {lohko['leveys']};"]
    for rek in kuvaus["rekisteri"]:
        rivit.append(f'    reg {{ name = "{rek["kuvaus"]}";')
        for k in rek["kentta"]:
            ylin, alin = k["bitit"]
            nollaus = f" = {k['nollaus']}" if "nollaus" in k else (
                "" if k["paasy"] == "ro" else " = 0")
            rivit.append(f"        field {{ {PAASY[k['paasy']]} }} "
                         f"{k['nimi']}[{ylin}:{alin}]{nollaus};")
        rivit.append(f"    }} {rek['nimi']} @ {rek['osoite']:#x};")
    return "\n".join(rivit + ["};", ""])
# @loppu muunnos


def avain(r: Rekisteri) -> list[tuple[str, int, int, int, str, int | None]]:
    return [(f"{r.polku}.{k.nimi}", r.osoite, k.msb, k.lsb, k.paasy,
             k.nollaus) for k in r.kentat]


def main() -> None:
    kuvaus = tomllib.loads((VERTAILU / "rekisterit.toml").read_text())
    rdl = muunna(kuvaus)
    print(f"muunnos: {len(rdl.splitlines())} rivia SystemRDL:aa, "
          "ensimmainen rekisteri:")
    for rivi in rdl.splitlines()[2:6]:
        print(f"  {rivi.strip()}")
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "muunnettu.rdl").write_text(rdl)
        muunnettu = rekisterit(kaanna("muunnettu.rdl", rdl=Path(tmp)))
    # @alku vertailu
    kasin = rekisterit(kaanna("ajastin.rdl"))
    a = [x for r in muunnettu for x in avain(r)]
    b = [x for r in kasin for x in avain(r)]
    print(f"muunnettu ja kasin kirjoitettu: {len(a)} kenttaa")
    print(f"  osoitteet, bitit, paasyt ja nollaukset: "
          f"{'samat' if a == b else 'EROAVAT'}")
    lisat = {f"{r.polku}.{k.nimi}": k.toiminnot for r in kasin
             for k in r.kentat if k.toiminnot}
    for nimi, toiminnot in lisat.items():
        print(f"  vain SystemRDL-kuvauksessa: {nimi} "
              f"{', '.join(toiminnot)}, sallinta CTRL.IE")
    # @loppu vertailu


if __name__ == "__main__":
    main()

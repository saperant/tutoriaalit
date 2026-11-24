#!/usr/bin/env python3
"""Käskyjä tai välimuistihutia operaatiota kohden Cachegrindilla.

  kaskyt.py [--tapahtuma Ir] [--toistot K] [--per M]
            [--suhde A B MIN]... OHJELMA TAPA...

Ohjelma ajetaan kullekin tavalle kahdesti: `OHJELMA --kerran TAPA 0`
ja `OHJELMA --kerran TAPA K`. Ohjelman on rakennettava sama syöte
kummassakin ajossa ja toistettava mitattavaa operaatiota annetun määrän
kertoja. Erotus jaettuna luvulla K * M on tapahtumien määrä operaatiota
kohden: käynnistys ja syötteen rakentaminen supistuvat pois.

Cachegrind laskee käskyt ja simuloi välimuistin deterministisesti,
joten tulos ei riipu koneen kuormasta. --suhde tarkistaa, että tavan A
tulos on vähintään MIN kertaa tavan B tulos.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

VALIMUISTI = ["--cache-sim=yes", "--D1=32768,8,64", "--LL=262144,8,64"]


def tapahtumat(ohjelma: str, tapa: str, toistot: int, valimuisti: bool,
               tiedosto: Path) -> dict[str, int]:
    komento = ["valgrind", "-q", "--tool=cachegrind",
               f"--cachegrind-out-file={tiedosto}",
               *(VALIMUISTI if valimuisti else ["--cache-sim=no"]),
               ohjelma, "--kerran", tapa, str(toistot)]
    # Valgrind varoittaa koneen omasta välimuistista, vaikka simuloitu
    # välimuisti on annettu; virheet näytetään vain, jos ajo epäonnistuu.
    ajo = subprocess.run(komento, check=False, stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE, text=True)
    if ajo.returncode != 0:
        sys.stderr.write(ajo.stderr)
        raise SystemExit(f"{' '.join(komento)}: paluuarvo {ajo.returncode}")
    nimet: list[str] = []
    arvot: list[int] = []
    for rivi in tiedosto.read_text("utf-8").splitlines():
        if rivi.startswith("events:"):
            nimet = rivi.split()[1:]
        elif rivi.startswith("summary:"):
            arvot = [int(x) for x in rivi.split()[1:]]
    return dict(zip(nimet, arvot))


def main() -> int:
    j = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    j.add_argument("--tapahtuma", default="Ir")
    j.add_argument("--toistot", type=int, default=10)
    j.add_argument("--per", type=int, default=1)
    j.add_argument("--suhde", nargs=3, action="append", default=[],
                   metavar=("A", "B", "MIN"))
    j.add_argument("ohjelma")
    j.add_argument("tavat", nargs="+")
    a = j.parse_args()

    valimuisti = a.tapahtuma != "Ir"
    tulos: dict[str, float] = {}
    with tempfile.TemporaryDirectory() as tmp:
        cg = Path(tmp) / "cg.out"
        for tapa in a.tavat:
            pohja = tapahtumat(a.ohjelma, tapa, 0, valimuisti, cg)
            koko = tapahtumat(a.ohjelma, tapa, a.toistot, valimuisti, cg)
            ero = koko[a.tapahtuma] - pohja[a.tapahtuma]
            tulos[tapa] = ero / (a.toistot * a.per)
            print(f"  {tapa:<22} {tulos[tapa]:10.1f} {a.tapahtuma}")

    for x, y, raja in a.suhde:
        suhde = tulos[x] / tulos[y] if tulos[y] else float("inf")
        if suhde < float(raja):
            print(f"VIRHE: {x}/{y} = {suhde:.2f} < {raja}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

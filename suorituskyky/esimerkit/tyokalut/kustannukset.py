#!/usr/bin/env python3
"""Valgrindin tulosten tiivistäjä ja tarkistin.

  kustannukset.py cachegrind TIEDOSTO [--tapahtumat Ir,D1mr] [RIVI...]
      [--suhde A B TAPAHTUMA MIN]...

RIVI on muotoa [nimi=][tiedosto:]funktio; oletustiedosto on TIEDOSTO.
  kustannukset.py callgrind [--rivit N] [--kumulatiivinen]  < annotaatio

cachegrind-tila lukee Cachegrindin raakatiedoston, laskee tapahtumat
funktioittain ja tulostaa taulukon annetuista funktioista. --suhde
tarkistaa, että A:n ja B:n tapahtumien suhde on vähintään MIN (Valgrindin
välimuistisimulaatio on deterministinen, joten tarkistus ei riipu koneen
kuormasta).

callgrind-tila tiivistää callgrind_annotate-tulosteen: polut ja
osoitteet poistetaan, ja jäljelle jäävät kustannus, osuus ja funktion
nimi.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict


def lue_cachegrind(polku: str) -> tuple[list[str], dict[str, list[int]]]:
    tapahtumat: list[str] = []
    summat: dict[str, list[int]] = defaultdict(list)
    funktio = "?"
    with open(polku, encoding="utf-8") as f:
        for rivi in f:
            if rivi.startswith("events:"):
                tapahtumat = rivi.split()[1:]
            elif rivi.startswith("fn="):
                # Kääntäjän kloonit (esim. f.constprop.0) lasketaan f:lle.
                funktio = rivi[3:].strip().split(".")[0]
            elif rivi[:1].isdigit():
                luvut = [int(x) for x in rivi.split()[1:]]
                s = summat[funktio]
                if not s:
                    s.extend([0] * len(tapahtumat))
                for i, x in enumerate(luvut):
                    s[i] += x
    return tapahtumat, summat


def cachegrind(argv: list[str]) -> int:
    polku = argv[0]
    valitut = ["Ir", "D1mr", "DLmr"]
    funktiot: list[str] = []
    suhteet: list[tuple[str, str, str, float]] = []
    i = 1
    while i < len(argv):
        if argv[i] == "--tapahtumat":
            valitut = argv[i + 1].split(",")
            i += 2
        elif argv[i] == "--suhde":
            a, b, t, m = argv[i + 1:i + 5]
            suhteet.append((a, b, t, float(m)))
            i += 5
        else:
            funktiot.append(argv[i])
            i += 1
    tiedostot: dict[str, tuple[list[str], dict[str, list[int]]]] = {}
    rivit: dict[str, tuple[str, str]] = {}
    for spec in funktiot:
        nimi, _, loput = spec.rpartition("=")
        tiedosto, _, funktio = loput.rpartition(":")
        tiedosto = tiedosto or polku
        rivit[nimi or funktio] = (tiedosto, funktio)
        if tiedosto not in tiedostot:
            tiedostot[tiedosto] = lue_cachegrind(tiedosto)

    def arvo(rivi: str, tapahtuma: str) -> int:
        tiedosto, funktio = rivit[rivi]
        tapahtumat, summat = tiedostot[tiedosto]
        if funktio not in summat:
            sys.exit(f"funktiota {funktio} ei löydy tiedostosta {tiedosto}")
        return summat[funktio][tapahtumat.index(tapahtuma)]

    print(f"  {'funktio':<26}" + "".join(f"{t:>14}" for t in valitut))
    for rivi in rivit:
        print(f"  {rivi:<26}"
              + "".join(f"{arvo(rivi, t):>14,}" for t in valitut))
    virheet = 0
    for a, b, t, minimi in suhteet:
        x, y = arvo(a, t), arvo(b, t)
        suhde = x / y if y else float("inf")
        if suhde < minimi:
            print(f"VIRHE: {t} {a}/{b} = {suhde:.2f} < {minimi}")
            virheet += 1
    return 1 if virheet else 0


ANNOTAATIO = re.compile(
    r"^\s*([\d,]+) \(\s*([\d.]+)%\)\s+(?:.*:)?([^\s:\[]+)(?: \[.*\])?$")


def callgrind(argv: list[str]) -> int:
    rivit = 8
    if "--rivit" in argv:
        rivit = int(argv[argv.index("--rivit") + 1])
    nahty: set[str] = set()
    tulos = []
    for rivi in sys.stdin:
        osuma = ANNOTAATIO.match(rivi.rstrip())
        if not osuma or "PROGRAM TOTALS" in rivi:
            continue
        maara, osuus, nimi = osuma.groups()
        if nimi.startswith("0x") or nimi in nahty or "below" in rivi:
            continue
        nahty.add(nimi)
        tulos.append(f"  {maara:>14} {float(osuus):6.1f} %  {nimi}")
    print("\n".join(tulos[:rivit]))
    return 0


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in ("cachegrind", "callgrind"):
        print(__doc__)
        return 2
    if sys.argv[1] == "cachegrind":
        return cachegrind(sys.argv[2:])
    return callgrind(sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())

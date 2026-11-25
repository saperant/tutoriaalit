"""Tekee ajoituskaavion JSONin esimerkin testatusta tulosteesta.

Käyttö: python3 kaaviot/tyokalut/tulosteesta.py KAAVIO TULOSTE.odotettu

Näin kirjan kaavio ja esimerkin tuloste eivät voi erkaantua: Makefile
tuottaa JSONin uudelleen ja vertaa sitä tallennettuun.
"""

import json
import sys


def aalto(bitit: str) -> str:
    """0/1-jono WaveDromin aalloksi: toistuva arvo on piste."""
    return "".join(c if i == 0 or c != bitit[i - 1] else "."
                   for i, c in enumerate(bitit))


def signaali(nimi: str, bitit: str) -> dict[str, str]:
    return {"name": nimi, "wave": aalto(bitit)}


def aaltorivit(osa: str) -> dict[str, str]:
    """Porttisimulaattorin aaltomuoto: rivit muotoa 'nimi 0011…'."""
    return dict(r.split() for r in osa.splitlines()
                if len(r.split()) == 2 and set(r.split()[1]) <= set("01"))


def hasardi(teksti: str) -> dict[str, object]:
    osat = teksti.split("\n\n")
    alku, korjattu = aaltorivit(osat[0]), aaltorivit(osat[1])
    signaalit = [signaali(n, alku[n]) for n in ("s", "s_n", "t0", "t1")]
    signaalit += [signaali("y", alku["y"]),
                  signaali("y + ab", korjattu["y"])]
    return {"signal": signaalit}


def sr_salpa(teksti: str) -> dict[str, object]:
    rivit = aaltorivit(teksti)
    return {"signal": [signaali(n, rivit[n]) for n in ("S", "R", "Q", "Qn")],
            "config": {"hscale": 0.45}}


def kiikut(teksti: str) -> dict[str, object]:
    """Taulukko 'aika clk d salpa kiikku': yksi rivi on yksi näyte."""
    sarakkeet = list(zip(*(r.split() for r in teksti.splitlines()[1:]),
                         strict=True))
    nimet = ["clk", "d", "salpa", "kiikku"]
    return {"signal": [signaali(n, "".join(s))
                       for n, s in zip(nimet, sarakkeet[1:], strict=True)]}


KAAVIOT = {"07-hasardi": hasardi, "08-sr-salpa": sr_salpa,
           "08-kiikut": kiikut}

if __name__ == "__main__":
    with open(sys.argv[2], encoding="utf-8") as f:
        print(json.dumps(KAAVIOT[sys.argv[1]](f.read()),
                         ensure_ascii=False))

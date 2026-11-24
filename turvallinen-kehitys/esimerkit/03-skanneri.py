"""Pieni salaisuusskanneri: tunnetut muodot, entropia ja poikkeukset.

Samat kolme keinoa ovat gitleaksin ja trufflehogin ytimessä. Skanneri
ajetaan commit-koukussa (luvun koukkuesimerkki) ja CI:ssä.
"""

import math
import re
from collections import Counter
from dataclasses import dataclass

# @alku saannot
# Avainmuodon alku kootaan osista, jotta tämä tiedosto ei itse näytä
# salaisuudelta muille skannereille.
YKSITYINEN = "-----BEGIN " + r"[A-Z ]*PRIVATE KEY-----"

SAANNOT: dict[str, re.Pattern[str]] = {
    "aws-avain": re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"),
    "yksityinen-avain": re.compile(YKSITYINEN),
    "tunnus-sijoitus": re.compile(
        r"(?i)(password|passwd|salasana|secret|token|api_?key)"
        r"\s*[:=]\s*[\"']([^\"']{8,})[\"']"),
}
SATUNNAINEN = re.compile(r"[A-Za-z0-9+/_\-]{24,}={0,2}")
POIKKEUS = "salaisuus-sallittu:"
# @loppu saannot


# @alku entropia
def entropia(s: str) -> float:
    """Shannonin entropia bitteinä merkkiä kohden."""
    n = len(s)
    return -sum(c / n * math.log2(c / n) for c in Counter(s).values())
# @loppu entropia


@dataclass(frozen=True)
class Loydos:
    tiedosto: str
    rivi: int
    saanto: str


# @alku skannaa
def skannaa(nimi: str, teksti: str) -> list[Loydos]:
    loydot = []
    for nro, rivi in enumerate(teksti.splitlines(), 1):
        if POIKKEUS in rivi:
            continue        # perusteltu poikkeus näkyy katselmoinnissa
        for saanto, malli in SAANNOT.items():
            osuma = malli.search(rivi)
            if osuma and (saanto != "tunnus-sijoitus"
                          or entropia(osuma.group(2)) > 3.0):
                loydot.append(Loydos(nimi, nro, saanto))
        for sana in SATUNNAINEN.findall(rivi):
            if entropia(sana) > 4.5:
                loydot.append(Loydos(nimi, nro, "korkea-entropia"))
    return loydot
# @loppu skannaa


TIEDOSTOT = {
    "asetukset.py": (
        'TIETOKANTA = "postgres://palvelu@db/tilaukset"\n'
        'API_KEY = "Xk9#mQ2vLp8wRt4z"\n'
        'AWS_AVAIN = "AKIAIOSFODNN7EXAMPLE"\n'
    ),
    "testit.py": (
        'SALASANA = "testisalasana"  '
        "# salaisuus-sallittu: testikannan kertakäyttötunnus\n"
        'password = "salasana"\n'
    ),
    "README.md": (
        "Koodattu teksti: dGhpcyBpcyBub3QgYSByZWFsIGtleSBhdCBhbGwhIQ==\n"
        "Käyttöavain: Z3q9VbX1mK7pL2wR8tY4nC6dF0hJ5sAe\n"
        "Rakenna komennolla make kaikki_tavoitteet_kerralla\n"
    ),
    "avain.pem": "-----BEGIN " + "OPENSSH PRIVATE KEY-----\n",
}


def main() -> None:
    kaikki = [lo for nimi, teksti in TIEDOSTOT.items()
              for lo in skannaa(nimi, teksti)]
    for lo in kaikki:
        print(f"{lo.tiedosto}:{lo.rivi}: {lo.saanto}")
    print(f"löydöksiä {len(kaikki)}")
    for s in ("salasana", "Xk9#mQ2vLp8wRt4z",
              "dGhpcyBpcyBub3QgYSByZWFsIGtleSBhdCBhbGwhIQ==",
              "Z3q9VbX1mK7pL2wR8tY4nC6dF0hJ5sAe"):
        print(f"entropia {entropia(s):.2f} b/merkki: {s[:20]}")


if __name__ == "__main__":
    main()

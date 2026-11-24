"""Uusien riippuvuuksien nimien tarkistus: kirjoitusvirhepaketit.

Hyökkääjä julkaisee suositun paketin nimeä muistuttavan paketin ja
odottaa kirjoitusvirhettä. Tarkistus ajetaan, kun riippuvuuslistaan
lisätään uusi nimi.
"""

import re

SUOSITUT = ("requests", "numpy", "django", "urllib3", "cryptography",
            "python-dateutil", "pyyaml", "setuptools")


# @alku etaisyys
def normalisoi(nimi: str) -> str:
    """PEP 503: kirjainkoko, '-', '_' ja '.' eivät erota nimiä."""
    return re.sub(r"[-_.]+", "-", nimi).lower()


def etaisyys(a: str, b: str) -> int:
    """Damerau–Levenshtein: lisäys, poisto, vaihto ja vierekkäinen
    vaihdos ovat kukin yksi muokkaus."""
    d = [[i + j if i * j == 0 else 0 for j in range(len(b) + 1)]
         for i in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            hinta = a[i - 1] != b[j - 1]
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1,
                          d[i - 1][j - 1] + hinta)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] \
                    and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
    return d[len(a)][len(b)]
# @loppu etaisyys


# @alku arvio
def arvioi(nimi: str) -> str:
    n = normalisoi(nimi)
    for suosittu in SUOSITUT:
        if n == suosittu:
            return "tunnettu paketti"
        if etaisyys(n, suosittu) <= 2 or n in (
                f"python-{suosittu}", f"{suosittu}-python", f"py{suosittu}"):
            return f"epäilyttävä: muistuttaa pakettia {suosittu}"
    return "ei osumaa; arvioi ylläpitäjä, ikä ja lataukset"
# @loppu arvio


def main() -> None:
    for nimi in ("Requests", "reqeusts", "nunpy", "python-numpy",
                 "djangoo", "PyYAML", "urllib", "pandas-extra"):
        print(f"{nimi:14} {arvioi(nimi)}")


if __name__ == "__main__":
    main()

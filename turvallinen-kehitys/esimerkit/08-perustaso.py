"""Löydösten perustaso: vanhat hyväksytyt, uudet estävät.

Kun analyysi otetaan käyttöön vanhaan koodiin, löydöksiä on satoja.
Perustaso (baseline) kirjaa olemassa olevat löydökset perusteluineen,
ja CI pysähtyy vain uusiin. Jokaisella poikkeuksella on syy ja
vanhenemispäivä, jotta perustasosta ei tule pysyvä roskakori.
"""

import hashlib
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Loydos:
    saanto: str
    tiedosto: str
    koodi: str          # rivin sisältö: rivinumero muuttuu, koodi harvoin

    @property
    def sormenjalki(self) -> str:
        avain = f"{self.saanto}|{self.tiedosto}|{self.koodi.strip()}"
        return hashlib.sha256(avain.encode()).hexdigest()[:12]


@dataclass(frozen=True)
class Poikkeus:
    sormenjalki: str
    syy: str
    voimassa: date


# @alku arvio
def arvioi(loydot: list[Loydos], perustaso: list[Poikkeus],
           tanaan: date) -> tuple[list[str], list[str]]:
    poikkeukset = {p.sormenjalki: p for p in perustaso}
    estavat, huomiot = [], []
    for lo in loydot:
        p = poikkeukset.pop(lo.sormenjalki, None)
        if p is None:
            estavat.append(f"uusi: {lo.saanto} {lo.tiedosto}")
        elif p.voimassa < tanaan:
            estavat.append(f"poikkeus vanhentunut: {lo.saanto} "
                           f"{lo.tiedosto} ({p.syy})")
    for p in poikkeukset.values():
        huomiot.append(f"korjattu, poista perustasosta: {p.syy}")
    return estavat, huomiot
# @loppu arvio


def main() -> None:
    vanha1 = Loydos("S324", "raportit.py", "hashlib.md5(data)")
    vanha2 = Loydos("S608", "haku.py", 'f"SELECT * FROM t WHERE {ehto}"')
    vanha3 = Loydos("S105", "testit.py", 'SALASANA = "testi"')
    perustaso = [
        Poikkeus(vanha1.sormenjalki, "md5 vain välimuistiavaimena",
                 date(2027, 6, 30)),
        Poikkeus(vanha2.sormenjalki, "korjataan tiketissä 412",
                 date(2026, 9, 30)),
        Poikkeus(vanha3.sormenjalki, "testikannan tunnus",
                 date(2027, 1, 31)),
    ]
    uusi = Loydos("S602", "vienti.py", "subprocess.run(k, shell=True)")
    # vanha3 on korjattu, uusi on ilmestynyt
    estavat, huomiot = arvioi([vanha1, vanha2, uusi], perustaso,
                              date(2026, 11, 24))
    for rivi in estavat:
        print("ESTÄÄ  ", rivi)
    for rivi in huomiot:
        print("HUOMIO ", rivi)
    print("CI:", "hylätty" if estavat else "hyväksytty")


if __name__ == "__main__":
    main()

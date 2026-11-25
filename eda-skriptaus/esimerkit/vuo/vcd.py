"""VCD-aaltomuototiedoston jäsennin ja näytteistys kellon reunalla.

VCD (Value Change Dump, IEEE 1364) on tekstimuoto: otsake nimeää
signaalit ja antaa kullekin lyhyen tunnuksen, ja runko luettelee
aikaleimat ja niillä muuttuneet arvot.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


# @alku malli
@dataclass
class Signaali:
    nimi: str                  # hierarkkinen nimi, esim. laskuri_tb.arvo
    leveys: int
    muutokset: list[tuple[int, str]] = field(default_factory=list)

    def arvo(self, aika: int) -> str:
        """Arvo hetkellä aika: viimeisin muutos ennen sitä tai sillä."""
        tulos = "x"
        for hetki, arvo in self.muutokset:
            if hetki > aika:
                break
            tulos = arvo
        return tulos
# @loppu malli


# @alku jasenna
def jasenna(polku: Path) -> dict[str, Signaali]:
    """Lukee VCD:n. Tuntematon rivi on virhe: jäsennin ei arvaa."""
    tunnukset: dict[str, list[Signaali]] = {}
    signaalit: dict[str, Signaali] = {}
    hierarkia: list[str] = []
    aika = 0
    otsake = True
    for rivi in polku.read_text().splitlines():
        osat = rivi.split()
        if not osat:
            continue
        if otsake:
            if osat[0] == "$scope":
                hierarkia.append(osat[2])
            elif osat[0] == "$upscope":
                hierarkia.pop()
            elif osat[0] == "$var":
                _, _, leveys, tunnus, nimi = osat[:5]
                s = Signaali(".".join([*hierarkia, nimi]), int(leveys))
                signaalit[s.nimi] = s
                tunnukset.setdefault(tunnus, []).append(s)
            elif osat[0] == "$enddefinitions":
                otsake = False
            continue
        if osat[0].startswith("#"):
            aika = int(osat[0][1:])
        elif osat[0][0] in "01xzXZ":              # skalaari: 1!
            for s in tunnukset[osat[0][1:]]:
                s.muutokset.append((aika, osat[0][0].lower()))
        elif osat[0][0] in "bB":                  # vektori: b101 !
            for s in tunnukset[osat[1]]:
                s.muutokset.append((aika, osat[0][1:].lower()))
        elif not osat[0].startswith("$"):         # $dumpvars, $end
            raise ValueError(f"tuntematon VCD-rivi: {rivi!r}")
    return signaalit
# @loppu jasenna


# @alku naytteet
def nousevat_reunat(kello: Signaali) -> list[int]:
    reunat, edellinen = [], "x"
    for hetki, arvo in kello.muutokset:
        if edellinen == "0" and arvo == "1":
            reunat.append(hetki)
        edellinen = arvo
    return reunat


def luku(arvo: str) -> int | None:
    """Binäärimerkkijono luvuksi; x ja z antavat None."""
    return int(arvo, 2) if set(arvo) <= {"0", "1"} else None


def naytteet(signaalit: dict[str, Signaali], kello: str,
             nimet: list[str]) -> list[dict[str, int | None]]:
    """Signaalien arvot juuri ennen kutakin kellon nousevaa reunaa:
    sen arvon, jonka kiikku reunalla näkee."""
    return [{n: luku(signaalit[n].arvo(reuna - 1)) for n in nimet}
            for reuna in nousevat_reunat(signaalit[kello])]
# @loppu naytteet

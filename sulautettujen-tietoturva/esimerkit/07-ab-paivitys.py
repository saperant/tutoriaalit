"""Päivityksen kestävyys sähkökatkoa vastaan.

Päivitys kirjoittaa flash-muistiin lohko kerrallaan. Katko voi tulla
minkä tahansa kirjoituksen jälkeen. Ohjelma kokeilee jokaisen
katkokohdan kahdelle menetelmälle ja kertoo, käynnistyykö laite
katkon jälkeen. Lopuksi kokeillaan päivitystä, joka on allekirjoitettu
oikein mutta kaatuu käynnistyessään.
"""

from collections.abc import Callable
from dataclasses import dataclass, field

LOHKOJA = 4


@dataclass
class Paikka:
    versio: int = 0
    lohkot: list[bool] = field(default_factory=lambda: [False] * LOHKOJA)
    otsake: bool = False        # kirjoitetaan viimeisenä

    def kelpaa(self) -> bool:   # vastaa allekirjoituksen tarkistusta
        return self.otsake and all(self.lohkot)


@dataclass
class Flash:
    paikat: dict[str, Paikka]
    aktiivinen: str = "A"
    kokeilu: str | None = None  # uusi kuva, jota ei vielä vahvistettu
    yrityksia: int = 0


def asennettu(versio: int) -> Paikka:
    return Paikka(versio, [True] * LOHKOJA, True)


Askel = Callable[[Flash], None]


# @alku paikallaan
def paikallaan(versio: int) -> list[Askel]:
    """Ainoa paikka pyyhitään ja kirjoitetaan uudelleen."""
    def pyyhi(f: Flash) -> None:
        f.paikat["A"] = Paikka()

    def lohko(i: int) -> Askel:
        return lambda f: f.paikat["A"].lohkot.__setitem__(i, True)

    def otsake(f: Flash) -> None:
        f.paikat["A"].versio, f.paikat["A"].otsake = versio, True

    return [pyyhi, *(lohko(i) for i in range(LOHKOJA)), otsake]
# @loppu paikallaan


# @alku ab
def ab(versio: int) -> list[Askel]:
    """Uusi kuva passiiviseen paikkaan; vaihto vasta kun se on ehjä."""
    def kohde(f: Flash) -> str:
        return "B" if f.aktiivinen == "A" else "A"

    def pyyhi(f: Flash) -> None:
        f.paikat[kohde(f)] = Paikka()

    def lohko(i: int) -> Askel:
        return lambda f: f.paikat[kohde(f)].lohkot.__setitem__(i, True)

    def otsake(f: Flash) -> None:
        p = f.paikat[kohde(f)]
        p.versio, p.otsake = versio, True

    def merkitse(f: Flash) -> None:   # yksi atominen kirjoitus
        f.kokeilu = kohde(f)

    return [pyyhi, *(lohko(i) for i in range(LOHKOJA)), otsake, merkitse]
# @loppu ab


# @alku kaynnistin
def kaynnista(f: Flash, kaatuu: set[int]) -> int | None:
    """Palauttaa käynnistyneen version tai None (laite ei käynnisty).
    Kokeilukuvalla on kolme yritystä; sen jälkeen palataan vanhaan."""
    for _ in range(5):          # vahtikoira käynnistää uudelleen
        if f.kokeilu and f.yrityksia < 3:
            f.yrityksia += 1
            nimi = f.kokeilu
        else:
            f.kokeilu, f.yrityksia = None, 0
            nimi = f.aktiivinen
        p = f.paikat[nimi]
        if not p.kelpaa():
            return None
        if p.versio in kaatuu:
            continue                          # kaatuu ennen vahvistusta
        if f.kokeilu == nimi:                 # sovellus vahvistaa itsensä
            f.aktiivinen, f.kokeilu, f.yrityksia = nimi, None, 0
        return p.versio
    return None
# @loppu kaynnistin


def koe(nimi: str, menetelma: Callable[[int], list[Askel]],
        kaatuu: set[int]) -> None:
    askeleet = menetelma(2)
    tulokset = []
    for katko in range(len(askeleet) + 1):
        f = Flash({"A": asennettu(1), "B": Paikka()})
        for askel in askeleet[:katko]:
            askel(f)
        v = kaynnista(f, kaatuu)
        tulokset.append("–" if v is None else str(v))
    toimii = sum(t != "–" for t in tulokset)
    print(f"{nimi:28} katkon jälkeen: {' '.join(tulokset)} "
          f"({toimii}/{len(tulokset)} käynnistyy)")


def main() -> None:
    print("Versio 1 asennettu, päivitetään versioon 2.")
    koe("Paikallaan", paikallaan, set())
    koe("A/B", ab, set())
    koe("Paikallaan, v2 kaatuu", paikallaan, {2})
    koe("A/B, v2 kaatuu", ab, {2})


if __name__ == "__main__":
    main()

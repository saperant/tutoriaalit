"""Deklaratiivinen malli: haluttu tila, suunnitelma ja täsmäytys.

Tila on sanakirja resurssin nimestä sen ominaisuuksiin. Suunnitelma on
haluttujen ja nykyisten tilojen erotus. Kun suunnitelma toteutetaan,
uusi suunnitelma on tyhjä: sama kuvaus voidaan ajaa uudelleen ilman
sivuvaikutuksia.
"""

from dataclasses import dataclass

Ominaisuudet = dict[str, str | int]
Tila = dict[str, Ominaisuudet]


# @alku suunnitelma
@dataclass(frozen=True)
class Muutos:
    laji: str                  # "luo", "muuta" tai "poista"
    nimi: str
    selite: str


def suunnittele(haluttu: Tila, nykyinen: Tila) -> list[Muutos]:
    """Vertaa tiloja ja palauttaa muutokset, joilla nykyinen korjataan."""
    muutokset = []
    for nimi in sorted(haluttu.keys() | nykyinen.keys()):
        uusi, vanha = haluttu.get(nimi), nykyinen.get(nimi)
        if uusi is None:
            muutokset.append(Muutos("poista", nimi, ""))
        elif vanha is None:
            muutokset.append(Muutos("luo", nimi, kuvaa(uusi)))
        elif uusi != vanha:
            erot = ", ".join(f"{k}: {vanha.get(k)} -> {uusi.get(k)}"
                             for k in sorted(uusi.keys() | vanha.keys())
                             if uusi.get(k) != vanha.get(k))
            muutokset.append(Muutos("muuta", nimi, erot))
    return muutokset


def toteuta(haluttu: Tila, nykyinen: Tila) -> list[Muutos]:
    """Toteuttaa suunnitelman: nykyinen tila muuttuu halutuksi."""
    muutokset = suunnittele(haluttu, nykyinen)
    for muutos in muutokset:
        if muutos.laji == "poista":
            del nykyinen[muutos.nimi]
        else:
            nykyinen[muutos.nimi] = dict(haluttu[muutos.nimi])
    return muutokset
# @loppu suunnitelma


def kuvaa(ominaisuudet: Ominaisuudet) -> str:
    return ", ".join(f"{k}={v}" for k, v in sorted(ominaisuudet.items()))


def tulosta(muutokset: list[Muutos]) -> None:
    if not muutokset:
        print("  ei muutoksia")
    for muutos in muutokset:
        selite = f" ({muutos.selite})" if muutos.selite else ""
        print(f"  {muutos.laji} {muutos.nimi}{selite}")

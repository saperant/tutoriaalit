"""Valmiin määritelmän tietoturvaehdot muutokselle.

Tiimi kirjaa tietoturvavaatimukset tarkistettaviksi säännöiksi. Sama
tarkistus ajetaan jokaiselle muutokselle, joten vaatimus ei unohdu
kiireessä eikä riipu siitä, kuka katselmoi.
"""

from collections.abc import Callable
from dataclasses import dataclass, field


# @alku muutos
@dataclass(frozen=True)
class Muutos:
    otsikko: str
    tiedostot: tuple[str, ...]
    testit_lisatty: bool
    uhkamalli_paivitetty: bool
    uudet_riippuvuudet: tuple[str, ...] = ()
    hyvaksyjat: frozenset[str] = field(default_factory=frozenset)
    tekija: str = ""
# @loppu muutos


# @alku saannot
Saanto = Callable[[Muutos], str | None]


def koskee(m: Muutos, *polut: str) -> bool:
    return any(t.startswith(polut) for t in m.tiedostot)


def todennus_vaatii_uhkamallin(m: Muutos) -> str | None:
    if koskee(m, "src/todennus/", "src/oikeudet/") \
            and not m.uhkamalli_paivitetty:
        return "todennusta tai oikeuksia muutettu: päivitä uhkamalli"
    return None


def muutos_vaatii_testit(m: Muutos) -> str | None:
    if koskee(m, "src/") and not m.testit_lisatty:
        return "koodia muutettu ilman testejä"
    return None


def riippuvuus_vaatii_arvion(m: Muutos) -> str | None:
    if m.uudet_riippuvuudet:
        nimet = ", ".join(m.uudet_riippuvuudet)
        return f"uudet riippuvuudet arvioitava: {nimet}"
    return None


def kaksi_silmaparia(m: Muutos) -> str | None:
    muut = m.hyvaksyjat - {m.tekija}
    if not muut:
        return "tarvitaan hyväksyntä joltakin muulta kuin tekijältä"
    return None


SAANNOT: tuple[Saanto, ...] = (
    todennus_vaatii_uhkamallin, muutos_vaatii_testit,
    riippuvuus_vaatii_arvion, kaksi_silmaparia,
)


def tarkista(m: Muutos) -> list[str]:
    return [v for s in SAANNOT if (v := s(m)) is not None]
# @loppu saannot


def main() -> None:
    muutokset = [
        Muutos("Kirjautumisen istuntoaika",
               ("src/todennus/istunto.py", "tests/test_istunto.py"),
               testit_lisatty=True, uhkamalli_paivitetty=False,
               hyvaksyjat=frozenset({"aino"}), tekija="aino"),
        Muutos("Raportin CSV-vienti",
               ("src/raportit/vienti.py", "tests/test_vienti.py"),
               testit_lisatty=True, uhkamalli_paivitetty=False,
               uudet_riippuvuudet=("csvkit",),
               hyvaksyjat=frozenset({"eero"}), tekija="aino"),
        Muutos("Dokumentaation korjaus", ("docs/asennus.md",),
               testit_lisatty=False, uhkamalli_paivitetty=False,
               hyvaksyjat=frozenset({"eero"}), tekija="aino"),
    ]
    for m in muutokset:
        puutteet = tarkista(m)
        tila = "valmis" if not puutteet else "kesken"
        print(f"{m.otsikko}: {tila}")
        for p in puutteet:
            print(f"  - {p}")


if __name__ == "__main__":
    main()

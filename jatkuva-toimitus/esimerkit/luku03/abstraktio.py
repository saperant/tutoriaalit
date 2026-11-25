"""Haarautuminen abstraktiolla: iso vaihdos pieninä askelina rungossa.

Vanha toteutus korvataan uudella ilman pitkää haaraa. Jokainen askel on
oma pieni muutoksensa, jonka jälkeen runko on julkaisukelpoinen.
"""

from typing import Protocol


# @alku rajapinta
class Hinnoittelu(Protocol):
    """Askel 1: abstraktio vanhan toteutuksen eteen. Käytös ei muutu."""

    def hinta(self, kappaleita: int) -> int: ...


class Portaat:
    """Vanha toteutus: kiinteät hintaportaat."""

    def hinta(self, kappaleita: int) -> int:
        yksikko = 100 if kappaleita < 10 else 90
        return kappaleita * yksikko


class Liukuva:
    """Askel 2: uusi toteutus kasvaa rungossa, mutta kukaan ei kutsu sitä."""

    def hinta(self, kappaleita: int) -> int:
        alennus = min(kappaleita // 5 * 2, 20)         # prosenttia
        return kappaleita * (100 - alennus)
# @loppu rajapinta


# @alku sopimus
def tayttaa_sopimuksen(toteutus: Hinnoittelu) -> bool:
    """Samat vaatimukset kummallekin: sopimustesti ajetaan molemmille."""
    hinnat = [toteutus.hinta(n) for n in range(0, 200)]
    return (hinnat[0] == 0 and hinnat[1] == 100
            and all(h >= 0 for h in hinnat)
            and all(h <= n * 100 for n, h in enumerate(hinnat)))


def valitse(uusi_kaytossa: bool) -> Hinnoittelu:
    """Askel 3: lippu valitsee toteutuksen. Askel 4 poistaa vanhan."""
    return Liukuva() if uusi_kaytossa else Portaat()
# @loppu sopimus


for nimi, toteutus in (("Portaat", Portaat()), ("Liukuva", Liukuva())):
    print(f"{nimi}: sopimus {'ok' if tayttaa_sopimuksen(toteutus) else 'EI'}")
for lippu in (False, True):
    hinnoittelu = valitse(lippu)
    print(f"lippu {'päällä' if lippu else 'pois':<7}"
          f"{type(hinnoittelu).__name__:<9}"
          f"50 kpl maksaa {hinnoittelu.hinta(50)}")

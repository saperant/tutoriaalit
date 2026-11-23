"""Dekoraattorit: uudelleenyritys ja välimuisti."""

import functools
from collections.abc import Callable


# @alku yrita
class TilapainenVirhe(Exception):
    """Virhe, jonka jälkeen kannattaa yrittää uudelleen."""


def yrita_uudelleen[**P, R](
    kertoja: int,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def koriste(funktio: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(funktio)
        def kaare(*args: P.args, **kwargs: P.kwargs) -> R:
            for yritys in range(1, kertoja + 1):
                try:
                    return funktio(*args, **kwargs)
                except TilapainenVirhe as virhe:
                    print(f"  yritys {yritys} epäonnistui: {virhe}")
            raise TilapainenVirhe(f"{funktio.__name__}: yritykset loppuivat")
        return kaare
    return koriste
# @loppu yrita


# @alku kaytto
kutsut = 0


@yrita_uudelleen(kertoja=3)
def hae_tila(palvelu: str) -> str:
    """Simuloi palvelua, joka vastaa vasta kolmannella kerralla."""
    global kutsut
    kutsut += 1
    if kutsut < 3:
        raise TilapainenVirhe("aikakatkaisu")
    return f"{palvelu}: OK"


print(hae_tila("tietokanta"))
print(hae_tila.__name__, hae_tila.__doc__)
# @loppu kaytto


# @alku cache
@functools.cache
def reitteja(rivit: int, sarakkeet: int) -> int:
    """Reittien määrä ruudukossa oikealle ja alas liikkuen."""
    if rivit == 0 or sarakkeet == 0:
        return 1
    return reitteja(rivit - 1, sarakkeet) + reitteja(rivit, sarakkeet - 1)


print(reitteja(16, 16), reitteja.cache_info().currsize)
# @loppu cache

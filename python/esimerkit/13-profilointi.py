"""cProfile: missä aika kuluu ja montako kertaa funktioita kutsutaan."""

import cProfile
import pstats
from functools import cache


def fib_naiivi(n: int) -> int:
    return n if n < 2 else fib_naiivi(n - 1) + fib_naiivi(n - 2)


@cache
def fib_muisti(n: int) -> int:
    return n if n < 2 else fib_muisti(n - 1) + fib_muisti(n - 2)


# @alku profiloi
def kutsumaarat(profiili: cProfile.Profile) -> dict[str, int]:
    """Funktioiden kokonaiskutsumäärät (ilman aikoja)."""
    tilasto = pstats.Stats(profiili)
    # Stats.stats: (tiedosto, rivi, funktio) -> (cc, nc, tt, ct, kutsujat)
    tiedot = tilasto.stats  # type: ignore[attr-defined]
    return {avain[2]: arvot[1] for avain, arvot in tiedot.items()
            if avain[2].startswith("fib")}


with cProfile.Profile() as profiili:
    fib_naiivi(20)
    fib_muisti(20)
print(kutsumaarat(profiili))
# @loppu profiloi

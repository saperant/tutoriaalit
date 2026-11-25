"""Totuustaulut ja loogiset ekvivalenssit tarkistettuina."""

from collections.abc import Callable
from itertools import product

Kaava = Callable[..., bool]


def implikaatio(p: bool, q: bool) -> bool:
    """p → q on epätosi vain, kun p on tosi ja q epätosi."""
    return (not p) or q


# @alku taulu
def totuustaulu(nimet: str, kaava: Kaava) -> None:
    """Tulostaa kaavan totuustaulun kaikilla muuttujien arvoilla."""
    muuttujat = nimet.split()
    print(" ".join(muuttujat), "| tulos")
    for arvot in product([False, True], repeat=len(muuttujat)):
        rivi = " ".join("1" if a else "0" for a in arvot)
        print(rivi, "|", int(kaava(*arvot)))


totuustaulu("p q", implikaatio)
# @loppu taulu


# @alku ekvivalenssi
def ekvivalentit(n: int, f: Kaava, g: Kaava) -> bool:
    """Ovatko kaavat samat kaikilla 2^n arvojen yhdistelmällä?"""
    return all(f(*a) == g(*a)
               for a in product([False, True], repeat=n))


def tautologia(n: int, f: Kaava) -> bool:
    return all(f(*a) for a in product([False, True], repeat=n))


lait: list[tuple[str, int, Kaava, Kaava]] = [
    ("De Morgan 1", 2, lambda p, q: not (p and q),
     lambda p, q: (not p) or (not q)),
    ("De Morgan 2", 2, lambda p, q: not (p or q),
     lambda p, q: (not p) and (not q)),
    ("osittelu", 3, lambda p, q, r: p and (q or r),
     lambda p, q, r: (p and q) or (p and r)),
    ("kontrapositio", 2, lambda p, q: implikaatio(p, q),
     lambda p, q: implikaatio(not q, not p)),
    ("käänteinen", 2, lambda p, q: implikaatio(p, q),
     lambda p, q: implikaatio(q, p)),
]
for nimi, n, f, g in lait:
    print(f"{nimi:<14} {'pätee' if ekvivalentit(n, f, g) else 'EI'}")

print("p ∨ ¬p tautologia:",
      tautologia(1, lambda p: p or not p))  # noqa: SIM221
# Päättelysäännöt: pätevä sääntö on tautologia, virhepäätelmä ei.
print("modus ponens tautologia:", tautologia(
    2, lambda p, q: implikaatio(p and implikaatio(p, q), q)))
print("modus tollens tautologia:", tautologia(
    2, lambda p, q: implikaatio((not q) and implikaatio(p, q), not p)))
print("seurauksen myöntäminen tautologia:", tautologia(
    2, lambda p, q: implikaatio(q and implikaatio(p, q), p)))
# @loppu ekvivalenssi

"""Jonosimulaattori analyyttisiä tuloksia vastaan kiinteällä siemenellä.

Tulostaa simuloidun ja analyyttisen viipymän ja niiden eron sekä
Littlen lain tarkistuksen. Ohjelma päättyy virheeseen, jos ero ylittää
toleranssin.
"""

import random
from collections.abc import Callable

from arkki.jonot import (Jono, eksponentiaalinen, mg1, mm1, mmc, simuloi,
                         vakio)

ASIAKKAAT = 400_000
TOLERANSSI = 0.06  # suhteellinen
S = 10.0  # palveluajan keskiarvo, ns


def main() -> None:
    # @alku tapaukset
    Jakauma = Callable[[float], Callable[[random.Random], float]]
    tapaukset: list[tuple[str, int, Callable[[float], Jono], Jakauma]] = [
        ("M/M/1", 1, lambda lam: mm1(lam, 1 / S), eksponentiaalinen),
        ("M/D/1", 1, lambda lam: mg1(lam, S, S * S), vakio),
        ("M/M/4", 4, lambda lam: mmc(lam, 1 / S, 4), eksponentiaalinen),
    ]
    print(f"{'jono':<6} {'rho':>4} {'W sim':>7} {'W anal':>7} {'ero':>6}"
          f" {'L':>6} {'lam*W':>6}")
    for nimi, c, analyysi, jakauma in tapaukset:
        for rho in (0.5, 0.8, 0.9):
            lam = rho * c / S
            m = simuloi(lam, jakauma(S), c, ASIAKKAAT, siemen=7)
            a = analyysi(lam)
            ero = m.viipyma / a.viipyma - 1
            # @loppu tapaukset
            print(f"{nimi:<6} {rho:>4} {m.viipyma:7.1f} {a.viipyma:7.1f}"
                  f" {ero:+6.1%} {m.maara:6.2f} {lam * m.viipyma:6.2f}")
            if abs(ero) > TOLERANSSI:
                raise SystemExit(f"{nimi} {rho}: ero {ero:+.1%} liian suuri")


if __name__ == "__main__":
    main()

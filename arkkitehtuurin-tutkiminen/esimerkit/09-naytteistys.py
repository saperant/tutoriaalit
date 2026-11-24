"""Satunnainen otanta ja latinalainen hyperkuutio, kun arviointeja on
vähän. Kumpaakin toistetaan 200 siemenellä, ja tulosta verrataan
täyden ruudukon optimiin."""

import random
from collections.abc import Callable

from arkki.siru import arvioi
from arkki.tutkimus import (Piste, Tila, latinalainen, ruudukko,
                            satunnainen)

TILA: Tila = {"r": [1, 2, 4, 8, 16], "c": [2, 4, 8, 16, 32],
        "v": [0.6, 0.7, 0.8, 0.9, 1.0, 1.1]}
TEHORAJA = 80.0
TOISTOJA = 200


# @alku arvo
def arvo(p: Piste) -> float:
    """Tavoite: nopeutus, jos tehoraja täyttyy, muuten 0."""
    t = arvioi(p["r"], p["c"], p["v"])
    return t.nopeutus if t.teho <= TEHORAJA else 0.0
# @loppu arvo


def main() -> None:
    optimi = max(arvo(p) for p in ruudukko(TILA))
    menetelmat: dict[str, Callable[[Tila, int, random.Random],
                                   list[Piste]]] = {
        "satunnainen": satunnainen, "hyperkuutio": latinalainen}
    print(f"ruudukon optimi {optimi:.2f} (150 arviointia)")
    print(f"{'menetelmä':<12} {'n':>3} {'vaje ka.':>9} {'vaje max':>9}"
          f" {'optimi löytyi':>14}")
    for n in (10, 20, 40):
        for nimi, menetelma in menetelmat.items():
            # @alku toistot
            vajeet = []
            for siemen in range(TOISTOJA):
                otos = menetelma(TILA, n, random.Random(siemen))
                vajeet.append(1 - max(arvo(p) for p in otos) / optimi)
            # @loppu toistot
            loytyi = sum(v < 1e-12 for v in vajeet) / TOISTOJA
            print(f"{nimi:<12} {n:>3} {sum(vajeet) / TOISTOJA:9.1%}"
                  f" {max(vajeet):9.1%} {loytyi:14.0%}")


if __name__ == "__main__":
    main()

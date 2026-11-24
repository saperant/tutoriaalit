"""Logiikkaporttien totuustaulut ja NAND-portin universaalisuus."""

from collections.abc import Callable
from itertools import product

Portti = Callable[[int, int], int]

# @alku portit
PORTIT: dict[str, Portti] = {
    "AND": lambda a, b: a & b,
    "OR": lambda a, b: a | b,
    "XOR": lambda a, b: a ^ b,
    "NAND": lambda a, b: 1 - (a & b),
    "NOR": lambda a, b: 1 - (a | b),
    "XNOR": lambda a, b: 1 - (a ^ b),
}
# @loppu portit


# @alku nand
def nand(a: int, b: int) -> int:
    return 1 - (a & b)


def ei(a: int) -> int:
    return nand(a, a)


def ja(a: int, b: int) -> int:
    return ei(nand(a, b))


def tai(a: int, b: int) -> int:
    return nand(ei(a), ei(b))            # De Morgan: a+b = (a'b')'


def xor(a: int, b: int) -> int:
    t = nand(a, b)                       # neljän NAND-portin XOR
    return nand(nand(a, t), nand(b, t))
# @loppu nand


def main() -> None:
    # @alku taulu
    print("a b | " + " ".join(f"{n:>4}" for n in PORTIT))
    for a, b in product((0, 1), repeat=2):
        arvot = " ".join(f"{f(a, b):>4}" for f in PORTIT.values())
        print(f"{a} {b} | {arvot}")
    # @loppu taulu

    # @alku tarkistus
    print()
    toteutukset: dict[str, Portti] = {"AND": ja, "OR": tai, "XOR": xor}
    for nimi, f in toteutukset.items():
        ok = all(f(a, b) == PORTIT[nimi](a, b)
                 for a, b in product((0, 1), repeat=2))
        print(f"{nimi} NAND-porteista: {'oikein' if ok else 'VÄÄRIN'}")
    ok = [ei(0), ei(1)] == [1, 0]
    print(f"NOT NAND-portista: {'oikein' if ok else 'VÄÄRIN'}")
    # @loppu tarkistus


if __name__ == "__main__":
    main()

"""Boolen algebran lait tarkistettuina ja kanoninen muoto
totuustaulusta."""

from collections.abc import Callable
from itertools import product

# @alku lait
Lauseke = Callable[[int, int, int], int]

LAIT: dict[str, tuple[Lauseke, Lauseke]] = {
    "De Morgan (ab)' = a'+b'": (
        lambda a, b, c: 1 - (a & b), lambda a, b, c: (1 - a) | (1 - b)),
    "osittelu a(b+c) = ab+ac": (
        lambda a, b, c: a & (b | c), lambda a, b, c: (a & b) | (a & c)),
    "osittelu a+bc = (a+b)(a+c)": (
        lambda a, b, c: a | (b & c), lambda a, b, c: (a | b) & (a | c)),
    "absorptio a+ab = a": (
        lambda a, b, c: a | (a & b), lambda a, b, c: a),
    "konsensus ab+a'c+bc = ab+a'c": (
        lambda a, b, c: (a & b) | ((1 - a) & c) | (b & c),
        lambda a, b, c: (a & b) | ((1 - a) & c)),
}


def sama(f: Lauseke, g: Lauseke) -> bool:
    """Kaksi lauseketta ovat samat, jos ne ovat samat kaikilla
    syötteillä: kolmella muuttujalla kahdeksan riviä."""
    return all(f(*x) == g(*x) for x in product((0, 1), repeat=3))
# @loppu lait


# @alku kanoninen
def mintermit(f: Lauseke) -> list[int]:
    return [i for i, x in enumerate(product((0, 1), repeat=3)) if f(*x)]


def summamuoto(f: Lauseke, nimet: str = "abc") -> str:
    """Kanoninen tulojen summa: yksi tulotermi jokaista ykkösriviä
    kohden."""
    termit = []
    for i in mintermit(f):
        bitit = format(i, "03b")
        termit.append("".join(n if b == "1" else n + "'"
                              for n, b in zip(nimet, bitit, strict=True)))
    return " + ".join(termit)
# @loppu kanoninen


def main() -> None:
    for nimi, (f, g) in LAIT.items():
        print(f"{nimi:31} {'pätee' if sama(f, g) else 'EI päde'}")

    # @alku enemmisto
    def enemmisto(a: int, b: int, c: int) -> int:
        return int(a + b + c >= 2)

    print()
    print(f"enemmistö: mintermit {mintermit(enemmisto)}")
    print(f"  kanoninen: {summamuoto(enemmisto)}")
    def sievennetty(a: int, b: int, c: int) -> int:
        return (a & b) | (a & c) | (b & c)

    tulos = "sama" if sama(enemmisto, sievennetty) else "eri"
    print(f"  sievennetty: ab + ac + bc ({tulos})")
    # @loppu enemmisto


if __name__ == "__main__":
    main()

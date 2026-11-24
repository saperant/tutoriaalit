"""C-rajapinnan laajennus: viitelaskenta ja virheet."""

import sys

import raaka


def main() -> None:
    print("summa:", raaka.summa([1.5, 2.5, 3]))
    print("generaattorista:", raaka.summa(x / 2 for x in range(5)))
    for huono in ([1.0, "kaksi"], 42):
        try:
            raaka.summa(huono)        # type: ignore[arg-type]
        except TypeError:
            print("TypeError:", repr(huono))

    # @alku viitteet
    olio = object()
    lista = [olio]
    ennen = sys.getrefcount(olio)
    for _ in range(100_000):
        palautettu = raaka.ensimmainen(lista)
        del palautettu
    print("viitemäärä ennallaan:", sys.getrefcount(olio) == ennen)
    print("sama olio:", raaka.ensimmainen(lista) is olio)
    # @loppu viitteet


if __name__ == "__main__":
    main()

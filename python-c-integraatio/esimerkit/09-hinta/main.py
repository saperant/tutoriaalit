"""Kutsun hinta: rajan ylitys alkio kerrallaan vai erässä.

Ajat vaihtelevat koneittain, joten tuloste kertoo vain järjestyksen
väljin marginaalein. Lisäksi tulostetaan suhdeluvut virhevirtaan.
"""

import sys
import time
from collections.abc import Callable

import hinta
import numpy as np


def nopein(f: Callable[[], object], kerrat: int = 5) -> float:
    paras = float("inf")
    for _ in range(kerrat):
        alku = time.perf_counter()
        f()
        paras = min(paras, time.perf_counter() - alku)
    return paras


def main() -> None:
    # @alku mittaus
    taulukko = np.random.default_rng(5).random(200_000)
    lista: list[float] = taulukko.tolist()

    t_python = nopein(lambda: [x * x for x in lista])
    t_alkio = nopein(lambda: [hinta.nelio(x) for x in lista])
    t_lista = nopein(lambda: hinta.neliot_lista(lista))
    t_taulukko = nopein(lambda: hinta.neliot_taulukko(taulukko))
    # @loppu mittaus

    print(f"alkio/python {t_alkio / t_python:.1f}, "
          f"lista/taulukko {t_lista / t_taulukko:.1f}, "
          f"alkio/taulukko {t_alkio / t_taulukko:.0f}", file=sys.stderr)
    # @alku tulos
    print("C++-kutsu alkiota kohden hitaampi kuin Pythonin x*x:",
          t_alkio > t_python)
    print("listan muunnos yli 3 kertaa hitaampi kuin taulukko:",
          t_lista > 3 * t_taulukko)
    print("erä yli 20 kertaa nopeampi kuin alkio kerrallaan:",
          t_alkio > 20 * t_taulukko)
    # @loppu tulos
    tulos = hinta.neliot_taulukko(taulukko)
    print("tulokset samat:", bool(np.allclose(tulos, np.square(taulukko))))


if __name__ == "__main__":
    main()

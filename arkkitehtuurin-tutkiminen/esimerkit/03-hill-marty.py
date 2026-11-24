"""Hillin ja Martyn moniydinmallit: paras ydinkoko kolmella
rakenteella, kun sirulla on 64 perusytimen (BCE) pinta-ala."""

from collections.abc import Callable

from arkki.mallit import dynaaminen, epasymmetrinen, symmetrinen

N = 64
KOOT = [1, 2, 4, 8, 16, 32, 64]
RAKENTEET: dict[str, Callable[[float, float, float], float]] = {
    "symm.": symmetrinen,
    "epäsymm.": epasymmetrinen,
    "dynaam.": dynaaminen,
}


# @alku paras
def paras(malli: Callable[[float, float, float], float], f: float
          ) -> tuple[int, float]:
    """Ydinkoko r (BCE), joka maksimoi nopeutuksen, ja nopeutus."""
    tulokset = [(malli(f, N, r), r) for r in KOOT]
    nopeutus, r = max(tulokset)
    return r, nopeutus
# @loppu paras


def main() -> None:
    print(f"siru {N} BCE, perf(r) = sqrt(r); kussakin: paras r ja nopeutus")
    print(f"{'f':>6}" + "".join(f"{n:>16}" for n in RAKENTEET))
    for f in (0.5, 0.9, 0.975, 0.99, 0.999):
        solut = []
        for malli in RAKENTEET.values():
            r, s = paras(malli, f)
            solut.append(f"r={r:<3} {s:6.1f}")
        print(f"{f:>6}" + "".join(f"{s:>16}" for s in solut))
    # @alku taulukko
    f = 0.975
    print(f"\nf = {f}: nopeutus ydinkoon funktiona")
    print(f"{'r':>4}" + "".join(f"{n:>10}" for n in RAKENTEET))
    for r in KOOT:
        print(f"{r:>4}" + "".join(f"{m(f, N, r):10.1f}"
                                  for m in RAKENTEET.values()))
    # @loppu taulukko


if __name__ == "__main__":
    main()

"""Pareto-rintama: nopeutus ja teho ilman tehorajaa."""

from arkki.siru import arvioi
from arkki.tutkimus import Tila, pareto, ruudukko

TILA: Tila = {"r": [1, 2, 4, 8, 16], "c": [2, 4, 8, 16, 32],
        "v": [0.6, 0.7, 0.8, 0.9, 1.0, 1.1]}


def main() -> None:
    # @alku rintama
    pisteet = ruudukko(TILA)
    tulokset = [arvioi(p["r"], p["c"], p["v"]) for p in pisteet]
    # Molemmat tavoitteet minimoidaan: -nopeutus ja teho.
    rintama = pareto([(-t.nopeutus, t.teho) for t in tulokset])
    rintama.sort(key=lambda i: tulokset[i].teho)
    # @loppu rintama
    print(f"{len(rintama)} Pareto-optimaalista pistettä {len(pisteet)}:sta")
    print(f"{'r':>3} {'c':>3} {'v':>4} {'nopeutus':>9} {'teho W':>7}"
          f" {'nop./W':>7}")
    for i in rintama:
        p, t = pisteet[i], tulokset[i]
        print(f"{p['r']:>3} {p['c']:>3} {p['v']:>4} {t.nopeutus:9.2f}"
              f" {t.teho:7.1f} {t.nopeutus / t.teho:7.3f}")


if __name__ == "__main__":
    main()
